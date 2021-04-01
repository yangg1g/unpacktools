library out_grp;

uses
  Windows,
  ExtrDefs in '..\..\..\api\delphi\ExtrDefs.pas';


function Save(Params:PSaveGroupFileParams):BOOL; stdcall;
type
  THeader = record
   Id:array[1..12] of char;
   Count:dword;
  end;
  TFileHeader = record
   Name:array[1..12] of char;
   Size:dword;
  end;
var
  Header:THeader;
  FileHeader:TFileHeader;
  i, len, StartPos:integer;
  written:dword;
begin
  Result:= false;

  with Header do begin
    Id:= 'KenSilverman';
    Count:= Params^.Count;
  end;
  if not WriteFile(Params^.FileHandle, Header, SizeOf(THeader), written, nil) then exit;

  StartPos:= SizeOf(THeader);

  for i:=0 to Params^.Count-1 do begin
    if Params^.Stop then exit;
    with Params^.GetFile(i)^ do begin
      FillChar(FileHeader, SizeOf(TFileHeader),0);
      len:= Length(Name);
      if len > SizeOf(FileHeader.Name) then len:= SizeOf(FileHeader.Name);
      Move(Name^, FileHeader.Name, len);
      FileHeader.Size:=Size;
      if not WriteFile(Params^.FileHandle, FileHeader, SizeOf(TFileHeader), written, nil) then exit;
      inc(StartPos, SizeOf(TFileHeader));
    end;
  end;

  for i:=0 to Params^.Count-1 do begin
    if Params^.Stop then exit;
    with Params^.GetFile(i)^ do begin
      Params^.SetInfo(Name);
      if not Params^.ExtractFile(i, StartPos) then begin
        exit;
      end;
      inc(StartPos,Size);
      inc(Params^.FileDone, Size);
      Params^.ShowStatus;
    end;
  end;

  Result:= true;
end;

procedure About(Handle:HWND); stdcall;
begin
  MessageBox(Handle, 'Duke Nukem 3D pack plugin', 'Information', MB_OK);
end;

var
  Plugin:TPluginInfo = (
    Version:     API_VER;
    FormatType:  FT_GROUPFILE;
    Ext:         'GRP';
    Description: 'Duke Nukem 3D pack';
    Priority:    1;
    TestProc:    nil;
    WorkProc:    @Save;
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
