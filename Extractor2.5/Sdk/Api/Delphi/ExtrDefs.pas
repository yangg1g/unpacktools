unit ExtrDefs;

interface

uses
  Windows;


const
  API_VER = 13;

  FT_UNKNOWN    = 0;
  FT_GRAPHICS   = 1;
  FT_VIDEO      = 2;
  FT_SOUND      = 4;
  FT_MODULE     = 8;
  FT_MIDI       = 16;
  FT_FONT       = 32;
  FT_SPECIAL    = 64;
  FT_GROUPFILE  = 4096;

type
  PLoadFormatParams = ^TLoadFormatParams;
  TLoadFormatParams = record
    FileHandle: THandle;
    SourceFileSize: int64;
    FileStartPos: int64;
    FileSize: int64;
    FileExt: pchar;
    FileInfo: pchar;
  end;

  TShowStatus = procedure(); stdcall;
  TAddFile = function (Source, Name: pchar; Pos, Size: int64; Info: pchar; Flag: dword): BOOL; stdcall;

  PLoadGroupfileParams = ^TLoadGroupfileParams;
  TLoadGroupfileParams = record
    FileHandle: THandle;
    FileName: pchar;
    Stop: BOOL;
    FileDone: int64;
    AddFile: TAddFile;
    ShowStatus: TShowStatus;
  end;

  PGetFileInfo = ^TGetFileInfo;
  TGetFileInfo = record
    Name: pchar;
    Source: pchar;
    Size: int64;
    Pos: int64;
    Info: pchar;
  end;

  TGetFile = function (Index: integer): PGetFileInfo; stdcall;
  TExtractFile = function (Index: integer; Pos: int64): BOOL; stdcall;
  TSetInfo = procedure (Info: pchar); stdcall;

  PSaveGroupfileParams = ^TSaveGroupfileParams;
  TSaveGroupfileParams = record
    FileHandle: THandle;
    FileName: pchar;
    Count: dword;
    Stop: BOOL;
    FileDone: int64;
    GetFile: TGetFile;
    ExtractFile: TExtractFile;
    SetInfo: TSetInfo;
    ShowStatus: TShowStatus;
  end;

  PPluginInfo = ^TPluginInfo;
  TPluginInfo = record
    Version: dword;
    FormatType: dword;
    Ext: pchar;
    Description: pchar;
    Priority: integer;
    TestProc: pointer;
    WorkProc: pointer;
    AboutProc :pointer;
    ConfigProc: pointer;
  end;

  PServiceProcs = ^ TServiceProcs;
  TServiceProcs = record
    ReadInteger: function (Section, Ident: pchar; Default: integer): integer; stdcall;
    WriteInteger: procedure (Section, Ident: pchar; Value: integer); stdcall;
    ReadFloat: function (Section, Ident: pchar; Default: double): double; stdcall;
    WriteFloat: procedure (Section, Ident: pchar; Value: double); stdcall;
    ReadBool: function (Section, Ident: pchar; Default: BOOL): BOOL; stdcall;
    WriteBool: procedure (Section, Ident: pchar; Value: BOOL); stdcall;
    ReadString: procedure (Section, Ident: pchar; Default: pchar; Buffer: pchar; BufferSize: dword); stdcall;
    WriteString: procedure (Section, Ident: pchar; Value: pchar); stdcall;
  end;

  TGetPluginInfoProc = function (ServiceProcs: PServiceProcs): PPluginInfo; stdcall;
  TTestProc = function (Buf: pointer): BOOL; stdcall;
  TLoadFormatProc = function (Params: PLoadFormatParams): BOOL; stdcall;
  TLoadGroupfileProc = function (Params: PLoadGroupfileParams): BOOL; stdcall;
  TSaveGroupfileProc = function (Params: PSaveGroupfileParams): BOOL; stdcall;
  TAboutProc = procedure (Handle: HWND); stdcall;
  TConfigProc = procedure (Handle: HWND); stdcall;


function Compare(buf: pointer; s: pchar; len: integer; pos:dword): BOOL;


implementation


function Compare(buf: pointer; s: pchar; len: integer; pos: dword): BOOL;
begin
  inc(dword(buf), pos);
  while (char(s^) = char(buf^)) do begin
    dec(len);
    if (len = 0) then break;
    inc(s);
    inc(dword(buf));
  end;
  Result:= (len = 0);
end;


end.

