#ifndef CatLockVersion
  #error CatLockVersion is not defined. Please pass /DCatLockVersion=<version> to ISCC.
#endif
[Setup]
AppName=CatLock
AppVersion={#CatLockVersion}
AppVerName=CatLock {#CatLockVersion}
DefaultDirName={userpf}\.catlock
DisableProgramGroupPage=yes
OutputDir=..\build
OutputBaseFilename=CatLockSetup
DefaultGroupName=CatLock
PrivilegesRequired=lowest
CloseApplications=force

[Files]
Source: "..\dist\CatLock\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\CatLock"; Filename: "{app}\CatLock.exe"
Name: "{userdesktop}\CatLock"; Filename: "{app}\CatLock.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
Name: "startup"; Description: "Add CatLock to Windows startup"; GroupDescription: "Startup options:"

[Registry]
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "CatLock"; ValueData: """{app}\CatLock.exe"""; Flags: uninsdeletevalue; Tasks: startup

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"
Type: files; Name: "{userstartup}\CatLock.lnk"

[Run]
Filename: "https://catlock.app/about/"; Description: "Visit website"; Flags: postinstall shellexec skipifsilent

[Code]
var
  ErrorCode: Integer;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if (not WizardSilent) and (MsgBox('Do you want to start CatLock now?', mbConfirmation, MB_YESNO) = IDYES) then
    begin
      Exec(ExpandConstant('{app}\CatLock.exe'), '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
    end;
  end;
end;
