/***************************************************************************/
/*
** PSF-o-Cycle development system
**
** This is an example which demonstrates the basics of how to make a PSF
** driver stub and illustrates the format of the PSF_DRIVER_INFO block.
** It can be customized to create stubs for actual games (whether they use
** the SEQ/VAB library or not).
*/

#define DO_SEQ // will be set/unset inside the code generation routine

/*
** Define the location of the PSF driver stub.
** You should define this to somewhere safe where there's no useful data and
** which will not get overwritten by the BSS clear loop.
*/
#define PSFDRV_LOAD       (0x80100000)
#define PSFDRV_SIZE       (0x00001000)
#define PSFDRV_PARAM      (0x80101000)
#define PSFDRV_PARAM_SIZE (0x00000100)

/*
** You can also define locations of game-specific data here.
*/
#define MY_SEQ      (0x80120000)
#define MY_SEQ_SIZE (0x00010000)
#define MY_VH       (0x80130000)
#define MY_VH_SIZE  (0x00010000)
#define MY_VB       (0x80140000)
#define MY_VB_SIZE  (0x00070000)

/*
** Parameters - you can make up any parameters you want within the
** PSFDRV_PARAM block.
** In this example, I'm including the sequence volume, reverb type and depth.
*/
#define PARAM_SEQVOL   (*((unsigned char*)(PSFDRV_PARAM+0x0000)))
#define PARAM_RTYPE    (*((unsigned char*)(PSFDRV_PARAM+0x0004)))
#define PARAM_RDEPTH   (*((unsigned char*)(PSFDRV_PARAM+0x0008)))

#ifndef DO_SEQ

#define PARAM_TICKMODE (*((unsigned char*)(PSFDRV_PARAM+0x000C)))
#define PARAM_LOOPOFF  (*((unsigned char*)(PSFDRV_PARAM+0x0010)))
#define PARAM_SEQNUM   (*((unsigned char*)(PSFDRV_PARAM+0x0014)))
#define PARAM_MAXSEQ   (*((unsigned char*)(PSFDRV_PARAM+0x0018)))

#endif

/***************************************************************************/
/*
** Entry point
*/
int psfdrv(void);
int psfdrv_entry(void) {
  /*
  ** Read the entire driver area, to ensure it doesn't get thrown out by
  ** PSFLab's optimizer
  */
  int *a = ((int*)(PSFDRV_LOAD));
  int *b = ((int*)(PSFDRV_LOAD+PSFDRV_SIZE));
  int c = 0;
  while(a < b) { c += (*a++); }
  /* This return value is completely ignored. */
  return c + psfdrv();
}

/***************************************************************************/

#define ASCSIG(a,b,c,d) ( \
  ((((unsigned long)(a)) & 0xFF) <<  0) | \
  ((((unsigned long)(b)) & 0xFF) <<  8) | \
  ((((unsigned long)(c)) & 0xFF) << 16) | \
  ((((unsigned long)(d)) & 0xFF) << 24)   \
  )

/***************************************************************************/
/*
** PSF_DRIVER_INFO block.
*/
unsigned long driverinfo[] = {
  /*
  ** Signature
  */
  ASCSIG('P','S','F','_'),
  ASCSIG('D','R','I','V'),
  ASCSIG('E','R','_','I'),
  ASCSIG('N','F','O',':'),
  /*
  ** Driver load address (was #defined earlier)
  */
  PSFDRV_LOAD,
  /*
  ** Driver entry point
  */
  (int)psfdrv_entry,
  /*
  ** Driver text string.  This should include the name of the game.
  */
  (int)"Duke Nukem Forever psf driver v1.0",
  /*
  ** Original EXE filename and CRC - ignore if zero
  **
  ** You may not want to use the exact original EXE here.  Sometimes you may
  ** want to patch the BSS clearing loop first, to ensure that it doesn't
  ** overwrite your driver stub, SEQ data, or other data that you added after
  ** the fact.  In this case I usually use a different name for the patched
  ** EXE, i.e. "ff8patch.exe" for Final Fantasy 8, and redo the CRC
  ** accordingly.
  */
  (int)"SLUS_999.99", 0x00000000,
  /*
  ** Jump patch address
  ** You should change this to point to the address of the "jal main"
  ** instruction in the game's original EXE.
  */
  0x80012340,
  /*
  ** List of song-specific areas we DO NOT upgrade.
  ** This is a 0-terminated list of addresses and byte lengths.
  ** Mark the areas containing SEQ, VAB, or other song-specific data here.
  ** Marking the psfdrv parameter area here might also be a good idea.
  */
  MY_SEQ, MY_SEQ_SIZE,
  MY_VH, MY_VH_SIZE,
  MY_VB, MY_VB_SIZE,
  PSFDRV_PARAM, PSFDRV_PARAM_SIZE,
  0,
  /*
  ** List of parameters (name,address,bytesize)
  ** This is a 0-terminated list.
  */
  (int)"seqvol", (int)(&PARAM_SEQVOL), 1,
  (int)"rtype" , (int)(&PARAM_RTYPE ), 1,
  (int)"rdepth", (int)(&PARAM_RDEPTH), 1,
#ifndef DO_SEQ
  (int)"tickmode", (int)(&PARAM_TICKMODE), 1,
  (int)"loop_off", (int)(&PARAM_LOOPOFF ), 1,
  (int)"seqnum",   (int)(&PARAM_SEQNUM)  , 1,
  (int)"maxseq",   (int)(&PARAM_MAXSEQ)  , 1,
#endif
  0  
};

/***************************************************************************/
/*
** Handy definitions
*/
#define NULL (0)

#define F0(x) (*((func0)(x)))
#define F1(x) (*((func1)(x)))
#define F2(x) (*((func2)(x)))
#define F3(x) (*((func3)(x)))
#define F4(x) (*((func4)(x)))
#define F5(x) (*((func5)(x)))
typedef int (*func0)(void);
typedef int (*func1)(int);
typedef int (*func2)(int,int);
typedef int (*func3)(int,int,int);
typedef int (*func4)(int,int,int,int);
typedef long (*func5)(long);

/*
** die() function - emits a break instruction.
** This isn't emulated in Highly Experimental, so it will cause the emulation
** to halt (this is a desired effect).
*/
unsigned long die_data[] = {0x4D};
#define die F0(die_data)

/*
** loopforever() - emits a simple branch and nop.
** Guaranteed to be detected as idle in H.E. no matter what the compiler
** does.
*/
unsigned long loopforever_data[] = {0x1000FFFF,0};
#define loopforever F0(loopforever_data)

#define ASSERT(x) { if(!(x)) { die(); } }

/***************************************************************************/
/*
** Library call addresses.
**
** You'll want to fill in the proper addresses for these based on what you
** found in IDA Pro or similar.
**
** I left some numbers from a previous rip in here just to make the example
** look pretty.  Trust me, you will want to change these.
*/  
  #define ResetCallback                          F0(0x80035440)

  #define SsInit                                 F0(0x80038838)
  #define SsSeqOpen(a,b)               ((short)( F2(0x80036618) ((int)(a),(int)(b)) ))
  #define SsSeqPlay(a,b,c)                       F3(0x8003998C) ((int)(a),(int)(b),(int)(c))
  #define SsSetMVol(a,b)                         F2(0x80036290) ((int)(a),(int)(b))
  #define SsStart                                F0(0x80038B9C)
  #define SsSetTableSize(a,b,c)                  F3(0x800396B0) ((int)(a),(int)(b),(int)(c))
  #define SsSetTickMode(a)                       F1(0x80039490) ((int)(a))
  #define SsSeqSetVol(a,b,c)                     F3(0x80039A40) ((int)(a),(int)(b),(int)(c))
  #define SsUtSetReverbType(a)         ((short)( F1(0x8003ADAC) ((int)(a)) ))
  #define SsUtReverbOn                           F0(0x8003AE5C)
  #define SsVabOpenHead(a,b)           ((short)( F2(0x8003A2B0) ((int)(a),(int)(b)) ))
  #define SsVabTransBodyPartly(a,b,c)  ((short)( F3(0x8003A7C4) ((int)(a),(int)(b),(int)(c)) ))
  #define SsVabTransCompleted(a)       ((short)( F1(0x8003A920) ((int)(a)) ))

  #define SpuSetReverb(a)                        F1(0x800418B4) ((int)(a))
  #define SpuSetReverbModeParam(a)               F1(0x80041A6C) ((int)(a))
  #define SpuSetReverbDepth(a)                   F1(0x8004244C) ((int)(a))
  #define SpuSetReverbVoice(a,b)                 F2(0x800424C4) ((int)(a),(int)(b))

  // alternatives
  #define SsVabOpenHeadSticky(a,b,c)   ((short)( F3(0x8009EEF8) ((int)(a),(int)(b),(int)(c)) ))
  #define SsVabTransBody(a,b)          ((short)( F2(0x8003A7C4) ((int)(a),(int)(b)) ))
  #define SpuIsTransferCompleted(a)    ((short)( F5(0x8003A920) ((long)(a)) ))
  #define SpuInit                                F0(0x80038838)
  #define SsStart2                               F0(0x80038B9C)
  
  // SEP functions
#ifndef DO_SEQ
  #define SsSepOpen(a,b,c)             ((short)( F3(0x800629D4) ((int)(a),(int)(b),(int)(c)) ))
  #define SsSepPlay(a,b,c,d)                     F4(0x80064F6C) ((int)(a),(int)(b),(int)(c),(int)(d))
#endif
/***************************************************************************/
/*
** PSF driver main() replacement
*/
int psfdrv(void) {
  void *seq, *vh, *vb;
  int vabid, seqid;
  int seqvol;
  int rtype;
  int rdepth;
#ifndef DO_SEQ  
  int tickmode;
  int loop_off;
  int seqnum;
  int maxseq; 
#endif   
  int r;

  seq = (void*)(MY_SEQ);
  vh  = (void*)(MY_VH);
  vb  = (void*)(MY_VB);

  /*
  ** Retrieve parameters and set useful defaults if they're zero
  */
  seqvol = PARAM_SEQVOL;
  rtype  = PARAM_RTYPE;
  rdepth = PARAM_RDEPTH;  
  if(!seqvol) seqvol = 127;
  if(!rtype)  rtype = 4;
  if(!rdepth) rdepth = 0x2A;

#ifndef DO_SEQ  
  tickmode = PARAM_TICKMODE;
  loop_off = PARAM_LOOPOFF;
  seqnum   = PARAM_SEQNUM;
  maxseq   = PARAM_MAXSEQ;  
  if(!seqnum)   seqnum     = 0;
  if(!tickmode) tickmode   = 4;  
#endif

  /*
  ** Initialize stuff
  */
  ResetCallback();

#ifdef SsInit
  SsInit();
#elif defined SpuInit
  SpuInit();
#endif  
  
  /* If the game originally used a predefined address for the SEQ table,
  ** you might want to set it here */
#define SSTABLE (0x801F0000)

#ifdef DO_SEQ
  SsSetTableSize(SSTABLE, 2, 1);
  SsSetTickMode(1);
#else
  SsSetTableSize(SSTABLE, 2, maxseq);
  SsSetTickMode(tickmode);
#endif    
  
#ifdef SsSetMVol  
  SsSetMVol(seqvol, seqvol);
#endif
  
  /*
  ** Reverb setup
  */
  

  { unsigned reverb_attr[5] = {7,0x100,0,0,0};
    reverb_attr[1] |= rtype;
    reverb_attr[2] = (rdepth << 8) | (rdepth << 24);

#ifdef SpuSetReverbModeParam
    SpuSetReverbModeParam(reverb_attr);
#endif
    
#ifdef SpuSetReverbDepth    
    SpuSetReverbDepth(reverb_attr);
#endif    
    
#ifdef SpuSetReverbVoice    
    SpuSetReverbVoice(1,0xFFFFFF); // turn all reverb voices on
#endif    
    
#ifdef SpuSetReverb   
    SpuSetReverb(1);
#elif defined SsUtReverbOn
    SsUtReverbOn();
#endif    
  }    

#ifdef SpuSetReverb   
    SpuSetReverb(1);
#elif defined SsUtReverbOn
    SsUtReverbOn();
#endif 

  
  /*
  ** Start sound engine
  */
#ifdef SsStart
  SsStart();
#elif defined SsStart2
  SsStart2();
#endif
  /*
  ** Open/transfer the VAB data
  */
#ifdef SsVabOpenHeadSticky  
  vabid = SsVabOpenHeadSticky(vh, 0, 0x1010);
#elif defined SsVabOpenHead  
  vabid = SsVabOpenHead(vh, -1);
#endif
  ASSERT(vabid >= 0);


#ifdef SsVabTransBodyPartly
  r = SsVabTransBodyPartly(vb, MY_VB_SIZE, vabid);
#elif defined SsVabTransBody
  r = SsVabTransBody(vb, vabid);
#endif
  ASSERT(r == vabid);

#ifdef SpuIsTransferCompleted
  r = SpuIsTransferCompleted(1);  
#elif defined SsVabTransCompleted
  r = SsVabTransCompleted(1);
#endif 
  ASSERT(r == 1);

  
#ifdef DO_SEQ
  // Open the SEQ
  seqid = SsSeqOpen(seq, vabid);
  ASSERT(seqid >= 0);

  //Play the seq
  SsSeqPlay(seqid, 1, 0);
#else
  // Open the SEP
  seqid = SsSepOpen(seq, vabid, maxseq);
  ASSERT(seqid >= 0);

  //Play the seq
  SsSepPlay(seqid, seqnum, 1, loop_off);
#endif

#ifdef SsSeqSetVol
  // Set its volume
  SsSeqSetVol(seqid, seqvol, seqvol);
#endif

  // Loop a while.
  loopforever();

  return 0;
}

/***************************************************************************/
