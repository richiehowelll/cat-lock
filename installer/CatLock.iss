[Setup]
AppName=CatLock
AppVersion=1.2.0
DefaultDirName={userpf}\.catlock
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=CatLockSetup
DefaultGroupName=CatLock
PrivilegesRequired=lowest
CloseApplications=force

[Files]
Source: "C:\Users\richi\PycharmProjects\CatLock\dist\CatLock.exe"; DestDir: "{userpf}\.catlock"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\CatLock"; Filename: "{userpf}\.catlock\catlock.exe"
Name: "{userdesktop}\CatLock"; Filename: "{userpf}\.catlock\catlock.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"
Name: "startup"; Description: "Add CatLock to Windows startup"; GroupDescription: "Startup options:"

[Registry]
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "CatLock"; ValueData: """{app}\catlock.exe"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{cmd}"; Parameters: "/C copy ""{userpf}\.catlock\catlock.exe"" ""{userstartup}\catlock.lnk"""; Flags: shellexec runhidden; Tasks: startup
Filename: https://catlock.app/about/; Description: "Visit website"; Flags: postinstall shellexec

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ErrorCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    if MsgBox('Do you want to start CatLock now?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(ExpandConstant('{userpf}\.catlock\catlock.exe'), '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
    end;
  end;
end;
