library fmt_wav;

uses
  Windows,
  ExtrDefs in '..\..\..\api\delphi\ExtrDefs.pas';


function Test(Buf:pointer):BOOL; stdcall;
begin
  Result:= (dword(pointer(dword(Buf)+8)^) = $45564157);
//  Result:= Compare(Buf, 'WAVE', 4, 8);
end;

function Load(Params:PLoadFormatParams):BOOL; stdcall;
type
  THeader = record
    Id:array[1..4] of char;
    Length:dword;
    WaveId:array[1..4] of char;
  end;
var
  Header:THeader;
  read:dword;
begin
  Result:= false;
  ReadFile(Params^.FileHandle, Header, SizeOf(THeader), read, nil);
  with Header do begin
    if not (Id = 'RIFF') then exit;
    Params^.FileSize:= Length + 8;
  end;
  Params^.FileInfo:= 'wav file information';  
  Params^.FileExt:= 'wav';
  Result:= true;
end;

procedure About(Handle:HWND); stdcall;
begin
  MessageBox(Handle, 'Windows Wave File Plugin', 'Information', MB_OK);
end;

var
  Plugin:TPluginInfo = (
    Version:	 API_VER;
    FormatType:  FT_SOUND;
    Ext:         'WAV';
    Description: 'Windows Wave File';
    Priority:    85;
    TestProc:    @Test;
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

