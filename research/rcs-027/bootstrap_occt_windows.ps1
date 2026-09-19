$ErrorActionPreference = "Stop"

$ExpectedCommit = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42"
$ExpectedVersion = "8.0.1"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DepsRoot = if ($env:RCS027_DEPS_ROOT) { $env:RCS027_DEPS_ROOT } else { Join-Path $RepoRoot ".deps\rcs027" }
$SourceDir = Join-Path $DepsRoot "occt-src"
$BuildDir = Join-Path $DepsRoot "occt-build"
$InstallDir = if ($env:RCS027_OCCT_PREFIX) { $env:RCS027_OCCT_PREFIX } else { Join-Path $DepsRoot "occt-8.0.1-win" }
$Jobs = if ($env:RCS027_BUILD_JOBS) { $env:RCS027_BUILD_JOBS } else { "2" }
$EvidenceDir = if ($env:RCS027_EVIDENCE_DIR) { $env:RCS027_EVIDENCE_DIR } else { Join-Path $RepoRoot ".results\rcs027\windows-step" }
$BootstrapLog = Join-Path $EvidenceDir "bootstrap-occt.log"
$TranscriptLog = Join-Path $EvidenceDir "bootstrap-powershell-transcript.log"

$RequiredToolkits = @("TKernel","TKMath","TKG2d","TKG3d","TKGeomBase","TKBRep","TKGeomAlgo","TKTopAlgo","TKPrim","TKBO","TKShHealing","TKDE","TKXSBase","TKDESTEP")
$AdditionalToolkits = ($RequiredToolkits -join ";")

function Write-Diagnostic {
    param([Parameter(Mandatory=$true)][string]$Message)
    Write-Host $Message
    Add-Content -Path $BootstrapLog -Value $Message -Encoding utf8
}

function Invoke-NativeLogged {
    param(
        [Parameter(Mandatory=$true)][string]$Label,
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$false)][string[]]$ArgumentList = @()
    )
    Write-Diagnostic $Label
    Add-Content -Path $BootstrapLog -Value ("> {0} {1}" -f $FilePath, ($ArgumentList -join " ")) -Encoding utf8
    & $FilePath @ArgumentList 2>&1 | Tee-Object -FilePath $BootstrapLog -Append
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -ne 0) { throw "$Label failed: $ExitCode" }
}

function Test-Install {
    # The RCS-022 shared harness consumes the deterministic Unix-style OCCT
    # install layout on every host: include/opencascade, lib and bin.  OCCT's
    # native Windows layout uses inc and win64/<compiler>/lib instead, so the
    # bootstrap explicitly selects INSTALL_DIR_LAYOUT=Unix below.
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

New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
Set-Content -Path $BootstrapLog -Value "RCS-027 Windows OCCT bootstrap native-command log" -Encoding utf8
Start-Transcript -Path $TranscriptLog -Force | Out-Null
try {
    Write-Diagnostic "RCS-027 Windows OCCT bootstrap diagnostic log: $BootstrapLog"
    Write-Diagnostic "PowerShell transcript: $TranscriptLog"
    Write-Diagnostic "Expected commit: $ExpectedCommit"
    Write-Diagnostic "Expected version: $ExpectedVersion"
    Write-Diagnostic "Install prefix: $InstallDir"
    Write-Diagnostic "Install layout: Unix (deterministic cross-platform bin/lib/include paths)"
    Write-Diagnostic "Build jobs: $Jobs"

    if (Test-Install) {
        Write-Diagnostic "RCS-027 OCCT already installed at $InstallDir"
        Write-Diagnostic "RCS027_OCCT_PREFIX=$InstallDir"
        return
    }

    if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
    New-Item -ItemType Directory -Force -Path $DepsRoot | Out-Null

    if (-not (Test-Path (Join-Path $SourceDir ".git"))) {
        if (Test-Path $SourceDir) { Remove-Item -Recurse -Force $SourceDir }
        Invoke-NativeLogged -Label "Cloning OCCT repository" -FilePath "git" -ArgumentList @("clone","--filter=blob:none","--no-checkout","https://github.com/Open-Cascade-SAS/OCCT.git",$SourceDir)
    }
    Invoke-NativeLogged -Label "Fetching exact OCCT commit" -FilePath "git" -ArgumentList @("-C",$SourceDir,"fetch","--depth=1","origin",$ExpectedCommit)
    Invoke-NativeLogged -Label "Checking out exact OCCT commit" -FilePath "git" -ArgumentList @("-C",$SourceDir,"checkout","--detach",$ExpectedCommit)
    $ActualCommit = (git -C $SourceDir rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw "OCCT rev-parse failed: $LASTEXITCODE" }
    if ($ActualCommit -ne $ExpectedCommit) { throw "OCCT source pin mismatch: $ActualCommit" }

    if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }

    $ConfigureArgs = @(
        "-S", $SourceDir, "-B", $BuildDir, "-G", "Ninja",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX=$InstallDir",
        "-DINSTALL_DIR_LAYOUT=Unix",
        "-DINSTALL_DIR_WITH_VERSION=OFF",
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
    Invoke-NativeLogged -Label "Configuring exact OCCT worker profile" -FilePath "cmake" -ArgumentList $ConfigureArgs
    Invoke-NativeLogged -Label "Building exact OCCT worker profile" -FilePath "cmake" -ArgumentList @("--build",$BuildDir,"--parallel",$Jobs)
    Invoke-NativeLogged -Label "Installing exact OCCT worker profile" -FilePath "cmake" -ArgumentList @("--install",$BuildDir)

    if (-not (Test-Install)) { throw "OCCT installation is incomplete or is not exact 8.0.1 worker profile" }

    @"
repository=https://github.com/Open-Cascade-SAS/OCCT.git
commit=$ExpectedCommit
version=$ExpectedVersion
build_profile=release-shared-cxx17-worker-only-headless-windows-v3-unix-layout
install_layout=Unix
selected_toolkits=$AdditionalToolkits
compiler=MSVC-19.51
"@ | Set-Content -Encoding ascii (Join-Path $InstallDir "RCS027_SOURCE_PIN.txt")

    Write-Diagnostic "RCS027_OCCT_PREFIX=$InstallDir"
}
catch {
    Write-Diagnostic ("BOOTSTRAP FAILURE: " + $_.Exception.Message)
    throw
}
finally {
    Stop-Transcript | Out-Null
}
