
#include <windows.h>


#define API_VER         13

#define FT_UNKNOWN      0
#define FT_GRAPHICS     1
#define FT_VIDEO        2
#define FT_SOUND        4
#define FT_MODULE       8
#define FT_MIDI         16
#define FT_FONT         32
#define FT_SPECIAL      64
#define FT_GROUPFILE    4096 

typedef struct {
  HANDLE FileHandle;
  unsigned __int64 SourceFileSize;
  unsigned __int64 FileStartPos;
  unsigned __int64 FileSize;
  char *FileExt;
  char *FileInfo;
} TLoadFormatParams;

typedef struct {
  HANDLE FileHandle;
  char *FileName;
  BOOL Stop;
  unsigned __int64 FileDone;
  BOOL (__stdcall *AddFile)(char *Source, char *Name, unsigned __int64 Pos, unsigned __int64 Size, char *Info, DWORD Flag);
  void (__stdcall *ShowStatus)();
} TLoadGroupfileParams;

typedef struct {
  char *Name;
  char *Source;
  unsigned __int64 Size;
  unsigned __int64 Pos;
  char *Info;
} TGetFileInfo;

typedef struct {
  HANDLE FileHandle;
  char *FileName;
  DWORD Count;
  BOOL Stop;
  unsigned __int64 FileDone;
  TGetFileInfo* (__stdcall *GetFile)(int Index);
  BOOL (__stdcall *ExtractFile)(int Index, unsigned __int64 Pos);  
  void (__stdcall *SetInfo)(char *Info);
  void (__stdcall *ShowStatus)();
} TSaveGroupfileParams;

typedef struct {
  DWORD Version;
  DWORD FormatType;
  char *Ext;
  char *Description;
  int Priority;
  void *TestProc;
  void *WorkProc;
  void *AboutProc;
  void *ConfigProc;
} TPluginInfo;

typedef struct {
  int (__stdcall *ReadInteger)(char *Section, char *Ident, int Default);
  void (__stdcall *WriteInteger)(char *Section, char *Ident, int Value);
  double (__stdcall *ReadFloat)(char *Section, char *Ident, double Default);
  void (__stdcall *WriteFloat)(char *Section, char *Ident, double Value);
  BOOL (__stdcall *ReadBool)(char *Section, char *Ident, BOOL Default);
  void (__stdcall *WriteBool)(char *Section, char *Ident, BOOL Value);
  void (__stdcall *ReadString)(char *Section, char *Ident, char *Default, char *Buffer, DWORD BufferSize);
  void (__stdcall *WriteString)(char *Section, char *Ident, char *Value);
} TServiceProcs;

typedef TPluginInfo* (__stdcall *TGetPluginInfoProc)(TServiceProcs *ServiceProcs);
typedef BOOL (__stdcall *TTestProc)(void *Buf);
typedef BOOL (__stdcall *TLoadFormatProc)(TLoadFormatParams *Params);
typedef BOOL (__stdcall *TLoadGroupfileProc)(TLoadGroupfileParams *Params);
typedef void (__stdcall *TAboutProc)(HWND Handle);
typedef void (__stdcall *TConfigProc)(HWND Handle);


extern "C" BOOL Compare(void *buf, char *s, int len, int pos);

#define COMPARE(buf,s,len,pos)\
  char *_s = s; int _len = len;\
  (char *)buf += pos;\
  while (*_s == *((char *)(buf))) {\
    _len--;\
    if (_len == 0) break;\
    _s++;\
    ((char *)buf)++;\
  }\
  return _len == 0

  
