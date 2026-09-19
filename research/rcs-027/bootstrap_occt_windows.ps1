$ErrorActionPreference = "Stop"

$ExpectedCommit = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
$ExpectedVersion = "8.0.1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DepsRoot = if ($env:RCS027_DEPS_ROOT) { $env:RCS027_DEPS_ROOT } else { Join-Path $RepoRoot ".deps\rcs027" }
$SourceDir = Join-Path $DepsRoot "occt-src"
$BuildDir = Join-Path $DepsRoot "occt-build"
$InstallDir = if ($env:RCS027_OCCT_PREFIX) { $env:RCS027_OCCT_PREFIX } else { Join-Path $DepsRoot "occt-8.0.1-win" }
$Jobs = if ($env:RCS027_BUILD_JOBS) { $env:RCS027_BUILD_JOBS } else { "2" }

$RequiredToolkits = @("TKernel","TKMath","TKG2d","TKG3d","TKGeomBase","TKBRep","TKGeomAlgo","TKTopAlgo","TKPrim","TKBO","TKShHealing","TKDE","TKXSBase","TKDESTEP")
$AdditionalToolkits = ($RequiredToolkits -join ";")

function Test-Install {
    $Header = Join-Path $InstallDir "include\opencascade\Standard_Version.hxx"
    if (-not (Test-Path $Header)) { return $false }
    if (-not (Select-String -Path $Header -SimpleMatch '#define OCC_VERSION_COMPLETE "8.0.1"' -Quiet)) { return $false }
    foreach ($Toolkit in $RequiredToolkits) {
        if (-not (Test-Path (Join-Path $InstallDir "lib\$Toolkit.lib"))) {
            Write-Host "Missing required OCCT import library $Toolkit.lib"
            return $false
        }
    }
    return $true
}

if (Test-Install) {
    Write-Host "RCS-027 OCCT already installed at $InstallDir"
    Write-Host "RCS027_OCCT_PREFIX=$InstallDir"
    exit 0
}

if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
New-Item -ItemType Directory -Force -Path $DepsRoot | Out-Null

if (-not (Test-Path (Join-Path $SourceDir ".git"))) {
    if (Test-Path $SourceDir) { Remove-Item -Recurse -Force $SourceDir }
    git clone --filter=blob:none --no-checkout https://github.com/Open-Cascade-SAS/OCCT.git $SourceDir
}
git -C $SourceDir fetch --depth=1 origin $ExpectedCommit
git -C $SourceDir checkout --detach $ExpectedCommit
$ActualCommit = (git -C $SourceDir rev-parse HEAD).Trim()
if ($ActualCommit -ne $ExpectedCommit) { throw "OCCT source pin mismatch: $ActualCommit" }

if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }

$ConfigureArgs = @(
    "-S", $SourceDir, "-B", $BuildDir, "-G", "Ninja",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DCMAKE_INSTALL_PREFIX=$InstallDir",
    "-DBUILD_CPP_STANDARD=C++17",
    "-DBUILD_LIBRARY_TYPE=Shared",
    "-DBUILD_MODULE_FoundationClasses=OFF",
    "-DBUILD_MODULE_ModelingData=OFF",
    "-DBUILD_MODULE_ModelingAlgorithms=OFF",
    "-DBUILD_MODULE_ApplicationFramework=OFF",
    "-DBUILD_MODULE_DataExchange=OFF",
    "-DBUILD_MODULE_Visualization=OFF",
    "-DBUILD_MODULE_Draw=OFF",
    "-DBUILD_ADDITIONAL_TOOLKITS=$AdditionalToolkits",
    "-DUSE_TCL=OFF","-DUSE_TK=OFF","-DUSE_FREETYPE=OFF","-DUSE_FREEIMAGE=OFF",
    "-DUSE_TBB=OFF","-DUSE_VTK=OFF","-DUSE_OPENVR=OFF","-DUSE_RAPIDJSON=OFF",
    "-DUSE_DRACO=OFF","-DUSE_FFMPEG=OFF","-DUSE_EIGEN=OFF","-DUSE_OPENGL=OFF","-DUSE_XLIB=OFF"
)
& cmake @ConfigureArgs
if ($LASTEXITCODE -ne 0) { throw "OCCT configure failed: $LASTEXITCODE" }
& cmake --build $BuildDir --parallel $Jobs
if ($LASTEXITCODE -ne 0) { throw "OCCT build failed: $LASTEXITCODE" }
& cmake --install $BuildDir
if ($LASTEXITCODE -ne 0) { throw "OCCT install failed: $LASTEXITCODE" }

if (-not (Test-Install)) { throw "OCCT installation is incomplete or is not exact 8.0.1 worker profile" }

@"
repository=https://github.com/Open-Cascade-SAS/OCCT.git
commit=$ExpectedCommit
version=$ExpectedVersion
build_profile=release-shared-cxx17-worker-only-headless-windows-v1
selected_toolkits=$AdditionalToolkits
compiler=MSVC-19.51
"@ | Set-Content -Encoding ascii (Join-Path $InstallDir "RCS027_SOURCE_PIN.txt")

Write-Host "RCS027_OCCT_PREFIX=$InstallDir"
