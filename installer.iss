; Inno Setup script — turns the PyInstaller onedir build into a Windows installer.
;
; Build with:  iscc installer.iss     (run AFTER pyinstaller produces dist\HDMCattle)
; Produces:    Output\HDMCattleSetup.exe
;
; During installation the user is asked ONCE for the security passkey. It is
; verified against the embedded one-way hash; a wrong key stops installation. On
; success the hash is stored on the machine; the plaintext passkey is never saved.

#define AppName "HDM Cattle Management"
#define AppVer "1.0.0"
#define AppPublisher "Health Data Matrics"
#define AppExe "HDMCattle.exe"
#define PasskeyHash "a4222fc74e338c62d84c5747cbbaf479a04421f94c40b1b76424f36b8d8e71d1"

[Setup]
AppName={#AppName}
AppVersion={#AppVer}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\HDM Cattle Management
DefaultGroupName=HDM Cattle Management
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=HDMCattleSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile=cattle.ico
UninstallDisplayIcon={app}\{#AppExe}
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\HDMCattle\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\HDM Cattle Management"; Filename: "{app}\{#AppExe}"
Name: "{group}\Uninstall HDM Cattle Management"; Filename: "{uninstallexe}"
Name: "{autodesktop}\HDM Cattle Management"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch HDM Cattle Management now"; Flags: nowait postinstall skipifsilent

[Code]
var
  PasskeyPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  PasskeyPage := CreateInputQueryPage(wpWelcome,
    'Security passkey', 'Enter your installation passkey',
    'This software is protected. Please enter the passkey to install it. ' +
    'You will only be asked for this once, during installation.');
  PasskeyPage.Add('Passkey:', True);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = PasskeyPage.ID then
  begin
    if Lowercase(GetSHA256OfString(PasskeyPage.Values[0])) <> Lowercase('{#PasskeyHash}') then
    begin
      MsgBox('Incorrect passkey. Installation cannot continue.', mbCriticalError, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    SaveStringToFile(ExpandConstant('{app}\passkey.hash'),
                     Lowercase('{#PasskeyHash}'), False);
end;
