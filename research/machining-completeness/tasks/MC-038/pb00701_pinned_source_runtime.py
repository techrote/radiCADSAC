#!/usr/bin/env python3
"""Finite pinned source replay runtime; this is not a Python sandbox.

Only exact manifest project paths can be imported or read through the local
interfaces. Standard-library implementations remain trusted. Original project
source buffers are compiled unchanged, with original future directives and
assertions. The context owns and restores only unique private module entries.
"""
from __future__ import annotations

import builtins
from collections import Counter
import hashlib
import io
import json
import os
from pathlib import Path as RealPath, PurePosixPath
import re
import sys
import types
import uuid


class RuntimeRefusal(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise RuntimeRefusal(reason)


def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()


class ReadOnlyBytes(io.BytesIO):
    def writable(self):
        return False

    def write(self, *args, **kwargs):
        raise RuntimeRefusal("READ_ONLY_PINNED_STREAM")

    def writelines(self, *args, **kwargs):
        raise RuntimeRefusal("READ_ONLY_PINNED_STREAM")

    def truncate(self, *args, **kwargs):
        raise RuntimeRefusal("READ_ONLY_PINNED_STREAM")

    def getbuffer(self):
        return super().getbuffer().toreadonly()


class PinnedRuntime:
    MAX_FILES = 128
    MAX_FILE_BYTES = 1048576
    MAX_TOTAL_BYTES = 16777216
    MAX_READS = 65536
    PRIVATE_PREFIX = "_radicadsac_pinned_"
    _MISSING = object()

    def __init__(self, root, pins, aliases=None, *, namespace=None):
        self.root = RealPath(root).resolve()
        require(self.root.is_absolute(), "ABSOLUTE_REPOSITORY_ROOT_REQUIRED")
        require(type(pins) is dict and 1 <= len(pins) <= self.MAX_FILES, "MANIFEST_COUNT_OR_TYPE")
        self.pins = {}
        for relative, expected in pins.items():
            require(type(relative) is str and 0 < len(relative) <= 512 and
                    not PurePosixPath(relative).is_absolute() and
                    str(PurePosixPath(relative)) == relative and ".." not in PurePosixPath(relative).parts,
                    "CANONICAL_RELATIVE_MANIFEST_PATH_REQUIRED")
            require(type(expected) is str and re.fullmatch(r"[0-9a-f]{40}", expected) is not None,
                    "EXACT_GIT_BLOB_REQUIRED")
            require(relative.endswith((".py", ".json")), "UNREVIEWED_MANIFEST_FILE_KIND")
            self.pins[str(self.root / relative)] = expected
        self.code_paths = {path for path in self.pins if path.endswith(".py")}
        self.names = {PurePosixPath(path).stem: path for path in self.code_paths}
        require(len(self.names) == len(self.code_paths), "AMBIGUOUS_MODULE_STEM")
        require(all(name.isidentifier() and name not in sys.stdlib_module_names for name in self.names),
                "AMBIGUOUS_OR_NONCANONICAL_PROJECT_NAME")
        self.aliases = dict(self.names)
        aliases = {} if aliases is None else aliases
        require(type(aliases) is dict and len(aliases) <= self.MAX_FILES, "DYNAMIC_ALIAS_BUDGET")
        for alias, relative in aliases.items():
            require(type(alias) is str and len(alias) <= 128 and alias.isidentifier(), "DYNAMIC_ALIAS_NAME")
            path = self._normalize(relative)
            require(path in self.code_paths, "DYNAMIC_ALIAS_UNPINNED_PATH")
            require(alias not in self.aliases or self.aliases[alias] == path, "DYNAMIC_ALIAS_COLLISION")
            self.aliases[alias] = path
        self.namespace = namespace or self.PRIVATE_PREFIX + uuid.uuid4().hex
        require(type(self.namespace) is str and self.namespace.startswith(self.PRIVATE_PREFIX) and
                self.namespace.isidentifier() and len(self.namespace) <= 128, "PRIVATE_NAMESPACE_REQUIRED")
        self.modules = {}
        self.loading = set()
        self._buffers = {}
        self._registered = {}
        self._used = False
        self.active = False
        self.reads = Counter()
        self.imports = Counter()
        self.loaded_paths = []
        self.snapshot_bytes = 0
        self._snapshot_records = []
        self._ordinary_import = builtins.__import__
        self.Path = self._make_path_type()
        self.local_pathlib = types.ModuleType("pathlib")
        self.local_pathlib.Path = self.Path
        self.local_sys = types.ModuleType("sys")
        self.local_sys.__dict__.update(vars(sys))
        self.local_sys.path = list(sys.path)
        self.local_sys.meta_path = list(sys.meta_path)
        self.local_sys.path_hooks = list(sys.path_hooks)
        self.local_sys.path_importer_cache = dict(sys.path_importer_cache)
        self.local_sys.modules = dict(sys.modules)
        self.local_builtins = types.ModuleType("builtins")
        self.local_builtins.__dict__.update(vars(builtins))
        self.local_builtins.__import__ = self._import
        self.local_builtins.open = self.open
        util = types.ModuleType("importlib.util")
        util.spec_from_file_location = self._spec
        util.module_from_spec = lambda spec: self.load(spec.origin)
        self.local_importlib = types.ModuleType("importlib")
        self.local_importlib.util = util

    def _normalize(self, path):
        try:
            value = os.fspath(path)
        except TypeError as exc:
            raise RuntimeRefusal("PATH_STRING_REQUIRED") from exc
        require(type(value) is str and 0 < len(value) <= 4096, "BOUNDED_TEXT_PATH_REQUIRED")
        # Logical path normalization must not follow a replacement symlink
        # after the checked snapshot has been captured.
        if not PurePosixPath(value).is_absolute():
            value = str(self.root / value)
        return os.path.normpath(value)

    def __enter__(self):
        require(not self._used, "RUNTIME_IS_SINGLE_USE")
        self._used = True
        try:
            for path, expected in sorted(self.pins.items()):
                actual_path = RealPath(path)
                require(actual_path.resolve() == actual_path, "MANIFEST_SYMLINK_ALIAS_REFUSED")
                with actual_path.open("rb") as stream:
                    raw = stream.read(self.MAX_FILE_BYTES + 1)
                require(len(raw) <= self.MAX_FILE_BYTES, "DEPENDENCY_FILE_BYTE_BUDGET")
                self.snapshot_bytes += len(raw)
                require(self.snapshot_bytes <= self.MAX_TOTAL_BYTES, "DEPENDENCY_AGGREGATE_BYTE_BUDGET")
                require(git_blob(raw) == expected, "PINNED_DEPENDENCY_DRIFT:" + path)
                self._buffers[path] = raw
                self._snapshot_records.append({"path": str(actual_path.relative_to(self.root)),
                                               "git_blob": expected, "bytes": len(raw)})
        except BaseException:
            self._buffers.clear()
            self._snapshot_records.clear()
            raise
        self.active = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def _require_active(self):
        require(self.active, "PINNED_RUNTIME_NOT_ACTIVE")

    def close(self):
        for name in reversed(list(self._registered)):
            self._undo_registration(name)
        self.modules.clear()
        self.loading.clear()
        self._buffers.clear()
        self.active = False

    def read_bytes(self, path):
        self._require_active()
        resolved = self._normalize(path)
        require(resolved in self._buffers, "UNPINNED_PROJECT_READ:" + resolved)
        require(sum(self.reads.values()) < self.MAX_READS, "PROJECT_READ_CALL_BUDGET")
        self.reads[resolved] += 1
        return self._buffers[resolved]

    def read_text(self, path, encoding=None, errors=None):
        require(encoding in (None, "utf-8", "utf8", "ascii") and errors in (None, "strict"),
                "UNREVIEWED_TEXT_DECODING_POLICY")
        return self.read_bytes(path).decode(encoding or "utf-8", errors or "strict")

    def read_json(self, path):
        """Exact bounded JSON convenience for a manifest-listed data buffer.

        This method does not redirect caller reports into legacy proof inputs.
        A reconciliation still owns its typed report/source validation.
        """
        resolved = self._normalize(path)
        require(resolved.endswith(".json"), "JSON_DATA_PATH_REQUIRED")

        def pairs(items):
            result = {}
            for key, value in items:
                require(key not in result, "DUPLICATE_JSON_KEY")
                result[key] = value
            return result

        def integer(token):
            require(len(token.lstrip("-")) <= 78, "JSON_INTEGER_TOKEN_BUDGET")
            value = int(token)
            require(value.bit_length() <= 256, "JSON_INTEGER_BIT_BUDGET")
            return value

        def nonexact(_):
            raise RuntimeRefusal("NONEXACT_JSON_NUMBER")

        try:
            value = json.loads(self.read_bytes(resolved), object_pairs_hook=pairs,
                               parse_int=integer, parse_float=nonexact, parse_constant=nonexact)
        except (RecursionError, UnicodeError, json.JSONDecodeError) as exc:
            raise RuntimeRefusal("INVALID_OR_EXCESSIVE_JSON") from exc
        stack, count = [(value, 0)], 0
        while stack:
            item, depth = stack.pop()
            count += 1
            require(count <= 262144 and depth <= 64, "JSON_NODE_OR_DEPTH_BUDGET")
            if type(item) is dict:
                stack.extend((child, depth+1) for child in item.values())
            elif type(item) is list:
                stack.extend((child, depth+1) for child in item)
        return value

    def open(self, file, mode="r", buffering=-1, encoding=None, errors=None, newline=None,
             closefd=True, opener=None):
        require(type(mode) is str and mode in ("r", "rt", "rb"), "READ_ONLY_PROJECT_OPEN_REQUIRED")
        require(buffering == -1 and closefd is True and opener is None, "UNREVIEWED_OPEN_OPTIONS")
        require(encoding in (None, "utf-8", "utf8", "ascii") and errors in (None, "strict") and
                newline in (None, "", "\n", "\r", "\r\n"), "UNREVIEWED_TEXT_STREAM_OPTIONS")
        raw = ReadOnlyBytes(self.read_bytes(file))
        if mode == "rb":
            require(encoding is None and errors is None and newline is None, "BINARY_OPEN_TEXT_OPTIONS")
            return raw
        return io.TextIOWrapper(raw, encoding=encoding or "utf-8", errors=errors or "strict", newline=newline)

    def _make_path_type(self):
        runtime = self

        class PinnedPath(os.PathLike):
            __slots__ = ("_pure",)

            def __init__(self, *parts):
                require(len(parts) <= 128, "PATH_PART_BUDGET")
                self._pure = PurePosixPath(*(os.fspath(part) for part in parts))
                require(len(str(self._pure)) <= 4096, "PATH_TEXT_BUDGET")

            def __fspath__(self):
                return str(self._pure)

            def __str__(self):
                return str(self._pure)

            def __repr__(self):
                return "PinnedPath(" + repr(str(self._pure)) + ")"

            def __hash__(self):
                return hash(self._pure)

            def __eq__(self, other):
                if isinstance(other, PinnedPath):
                    return self._pure == other._pure
                if isinstance(other, PurePosixPath):
                    return self._pure == other
                return NotImplemented

            def __truediv__(self, other):
                return PinnedPath(self._pure / os.fspath(other))

            def __rtruediv__(self, other):
                return PinnedPath(PurePosixPath(other) / self._pure)

            @property
            def parent(self):
                return PinnedPath(self._pure.parent)

            @property
            def parents(self):
                return tuple(PinnedPath(path) for path in self._pure.parents)

            @property
            def name(self):
                return self._pure.name

            @property
            def stem(self):
                return self._pure.stem

            @property
            def suffix(self):
                return self._pure.suffix

            @property
            def parts(self):
                return self._pure.parts

            def as_posix(self):
                return self._pure.as_posix()

            def resolve(self, strict=False):
                require(type(strict) is bool, "RESOLVE_STRICT_TYPE")
                result = PinnedPath(runtime._normalize(self))
                if strict:
                    runtime.read_bytes(result)
                return result

            def absolute(self):
                return self.resolve()

            def is_absolute(self):
                return self._pure.is_absolute()

            def relative_to(self, other):
                return PinnedPath(self._pure.relative_to(os.fspath(other)))

            def with_name(self, name):
                return PinnedPath(self._pure.with_name(name))

            def with_suffix(self, suffix):
                return PinnedPath(self._pure.with_suffix(suffix))

            def joinpath(self, *parts):
                return PinnedPath(self._pure.joinpath(*(os.fspath(part) for part in parts)))

            def read_bytes(self):
                return runtime.read_bytes(self)

            def read_text(self, encoding=None, errors=None):
                return runtime.read_text(self, encoding, errors)

            def open(self, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
                return runtime.open(self, mode, buffering, encoding, errors, newline)

            def is_file(self):
                runtime.read_bytes(self)
                return True

            def exists(self):
                return self.is_file()

            def stat(self):
                return types.SimpleNamespace(st_size=len(runtime.read_bytes(self)))

            def write_bytes(self, *args, **kwargs):
                raise RuntimeRefusal("PROJECT_WRITES_NOT_ALLOWED")

            write_text = mkdir = unlink = rename = replace = touch = write_bytes

        return PinnedPath

    def private_name(self, path):
        resolved = self._normalize(path)
        require(resolved in self.code_paths, "UNPINNED_PRIVATE_MODULE_NAME")
        return self.namespace + "__" + PurePosixPath(resolved).stem

    def _register(self, module):
        name = module.__name__
        require(name.startswith(self.namespace + "__") and name not in self._registered,
                "PRIVATE_REGISTRATION_COLLISION")
        self._registered[name] = (sys.modules.get(name, self._MISSING),
                                  self.local_sys.modules.get(name, self._MISSING))
        sys.modules[name] = module
        self.local_sys.modules[name] = module

    def _undo_registration(self, name):
        previous, local_previous = self._registered.pop(name)
        if previous is self._MISSING:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
        if local_previous is self._MISSING:
            self.local_sys.modules.pop(name, None)
        else:
            self.local_sys.modules[name] = local_previous

    def load(self, path):
        self._require_active()
        resolved = self._normalize(path)
        require(resolved in self.code_paths, "UNPINNED_PROJECT_MODULE:" + resolved)
        if resolved in self.modules:
            return self.modules[resolved]
        require(resolved not in self.loading, "UNREVIEWED_CYCLIC_PROJECT_IMPORT:" + resolved)
        raw = self.read_bytes(resolved)
        module = types.ModuleType(self.private_name(resolved))
        module.__file__ = resolved
        module.__package__ = ""
        module.__dict__["__builtins__"] = dict(vars(self.local_builtins))
        self.loading.add(resolved)
        self._register(module)
        try:
            # Never inherit this runtime's future flags or optimize away
            # original assertions; source directives still apply normally.
            exec(compile(raw, resolved, "exec", dont_inherit=True, optimize=0), module.__dict__)
        except BaseException:
            self._undo_registration(module.__name__)
            raise
        finally:
            self.loading.remove(resolved)
        self.modules[resolved] = module
        self.loaded_paths.append(resolved)
        return module

    def _spec(self, name, path):
        self._require_active()
        resolved = self._normalize(path)
        require(type(name) is str and self.aliases.get(name) == resolved, "UNREVIEWED_DYNAMIC_ALIAS_OR_PATH")

        def execute(module):
            require(module is self.load(resolved), "DYNAMIC_CONSTRUCTOR_IDENTITY_CHANGED")

        return types.SimpleNamespace(name=name, origin=resolved,
                                     loader=types.SimpleNamespace(exec_module=execute))

    def _import(self, name, globals=None, locals=None, fromlist=(), level=0):
        self._require_active()
        require(type(name) is str and len(name) <= 256 and level == 0, "UNREVIEWED_IMPORT_NAME_OR_LEVEL")
        self.imports[name] += 1
        require(sum(self.imports.values()) <= self.MAX_READS, "IMPORT_CALL_BUDGET")
        if name in self.names:
            return self.load(self.names[name])
        if name == "pathlib":
            require(not fromlist or set(fromlist) <= {"Path"}, "UNREVIEWED_PATHLIB_INTERFACE")
            return self.local_pathlib
        if name == "sys":
            return self.local_sys
        if name == "builtins":
            return self.local_builtins
        if name in ("importlib", "importlib.util"):
            require(not fromlist or (name == "importlib" and set(fromlist) <= {"util"}),
                    "UNREVIEWED_IMPORTLIB_INTERFACE")
            return self.local_importlib
        require(not name.startswith("importlib."), "UNREVIEWED_IMPORTLIB_INTERFACE")
        root_name = name.split(".")[0]
        require(root_name in sys.stdlib_module_names or root_name in sys.builtin_module_names,
                "UNPINNED_NONSTDLIB_IMPORT:" + name)
        return self._ordinary_import(name, globals, locals, fromlist, level)

    def attestation(self):
        records = [dict(record) for record in self._snapshot_records]
        manifest_bytes = json.dumps(records, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True).encode("ascii")
        return {"declared_code_paths": len(self.code_paths),
                "declared_data_paths": len(self.pins)-len(self.code_paths),
                "captured_bytes": self.snapshot_bytes,
                "snapshots": records,
                "snapshot_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "loaded_project_modules": [str(RealPath(path).relative_to(self.root)) for path in self.loaded_paths],
                "read_counts": {str(RealPath(path).relative_to(self.root)): count for path, count in sorted(self.reads.items())},
                "source_buffers_compiled_without_cache": True,
                "read_buffers_identical_to_verified_snapshots": True,
                "standard_library_runtime_trusted": True,
                "python_sandbox_claimed": False}
