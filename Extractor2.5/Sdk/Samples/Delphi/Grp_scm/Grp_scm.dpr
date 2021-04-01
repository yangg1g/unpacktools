library grp_scm;

uses
  Windows,
  ExtrDefs in '..\..\..\api\delphi\ExtrDefs.pas';

  
function Load(Params:PLoadGroupFileParams):BOOL; stdcall;
var
  FileTableSize:dword;
  FileName:string;
  Size,Pos:dword;
  read:dword;
  c:char;
begin
  Result:= false;
  if not ReadFile(Params^.FileHandle, FileTableSize, SizeOf(FileTableSize), read, nil) then exit;
  Pos:= SizeOf(FileTableSize) + FileTableSize;
  Params^.FileDone:= SizeOf(FileTableSize);
  while FileTableSize > 0 do begin
    FileName:= '';
    repeat
      if not ReadFile(Params^.FileHandle, c, 1, read, nil) then exit;
      if c = #0 then break;
      FileName:= FileName + c;
    until false;
    if not ReadFile(Params^.FileHandle, Size, 4, read, nil) then exit;
    if Size > 0 then
      if not Params^.AddFile(Params^.FileName, FileName, Pos, Size, '', 0) then exit;
    inc(Pos, Size);
    dec(FileTableSize, Length(FileName) + 1 + 4);
    inc(Params^.FileDone, Length(FileName) + 1 + 4 + Size);
    Params^.ShowStatus;
  end;
  Result:=true;
end;

procedure About(Handle:HWND); stdcall;
begin
  MessageBox(Handle, 'ICQ Sound Scheme Plugin', 'Information', MB_OK);
end;

var
  Plugin:TPluginInfo = (
    Version:     API_VER;
    FormatType:  FT_GROUPFILE;
    Ext:         'SCM';
    Description: 'ICQ Sound Scheme';
    Priority:    2;
    TestProc:    nil;
    WorkProc:    @Load;
    AboutProc:   @About;
    ConfigProc:  nil;
  );

function GetPluginInfo(ServiceProcs:PServiceProcs):PPluginInfo; stdcall;
begin
  Result:= @Plugin;
end;


exports
  GetPluginInfo;

end.
