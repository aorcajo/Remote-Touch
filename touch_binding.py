from cffi import FFI

ffi = FFI()
ffi.cdef("""
typedef int BOOL;
typedef uint32_t UINT32;
typedef void *PVOID;
typedef PVOID HANDLE;
typedef HANDLE HWND;
typedef long LONG;
typedef unsigned long DWORD;
typedef signed int INT32;
typedef uint64_t UINT64;

typedef enum tagPOINTER_INPUT_TYPE { 
  PT_POINTER   = 0x00000001,
  PT_TOUCH     = 0x00000002,
  PT_PEN       = 0x00000003,
  PT_MOUSE     = 0x00000004,
  PT_TOUCHPAD  = 0x00000005
} POINTER_INPUT_TYPE;

typedef enum tagPOINTER_FLAGS { 
  POINTER_FLAG_NONE           = 0x00000000, // Default
  POINTER_FLAG_NEW            = 0x00000001, // New pointer
  POINTER_FLAG_INRANGE        = 0x00000002, // Pointer has not departed
  POINTER_FLAG_INCONTACT      = 0x00000004, // Pointer is in contact
  POINTER_FLAG_FIRSTBUTTON    = 0x00000010, // Primary action
  POINTER_FLAG_SECONDBUTTON   = 0x00000020, // Secondary action
  POINTER_FLAG_THIRDBUTTON    = 0x00000040, // Third button
  POINTER_FLAG_FOURTHBUTTON   = 0x00000080, // Fourth button
  POINTER_FLAG_FIFTHBUTTON    = 0x00000100, // Fifth button
  POINTER_FLAG_PRIMARY        = 0x00002000, // Pointer is primary
  POINTER_FLAG_CONFIDENCE     = 0x00004000, // Pointer is considered unlikely to be accidental
  POINTER_FLAG_CANCELED       = 0x00008000, // Pointer is departing in an abnormal manner
  POINTER_FLAG_DOWN           = 0x00010000, // Pointer transitioned to down state (made contact)
  POINTER_FLAG_UPDATE         = 0x00020000, // Pointer update
  POINTER_FLAG_UP             = 0x00040000, // Pointer transitioned from down state (broke contact)
  POINTER_FLAG_WHEEL          = 0x00080000, // Vertical wheel
  POINTER_FLAG_HWHEEL         = 0x00100000, // Horizontal wheel
  POINTER_FLAG_CAPTURECHANGED = 0x00200000, // Lost capture
  POINTER_FLAG_HASTRANSFORM   = 0x00400000
} POINTER_FLAGS;

typedef struct tagPOINT {
  LONG x;
  LONG y;
} POINT, *PPOINT;

typedef enum tagPOINTER_BUTTON_CHANGE_TYPE {
    POINTER_CHANGE_NONE,
    POINTER_CHANGE_FIRSTBUTTON_DOWN,
    POINTER_CHANGE_FIRSTBUTTON_UP,
    POINTER_CHANGE_SECONDBUTTON_DOWN,
    POINTER_CHANGE_SECONDBUTTON_UP,
    POINTER_CHANGE_THIRDBUTTON_DOWN,
    POINTER_CHANGE_THIRDBUTTON_UP,
    POINTER_CHANGE_FOURTHBUTTON_DOWN,
    POINTER_CHANGE_FOURTHBUTTON_UP,
    POINTER_CHANGE_FIFTHBUTTON_DOWN,
    POINTER_CHANGE_FIFTHBUTTON_UP,
} POINTER_BUTTON_CHANGE_TYPE;

typedef struct tagPOINTER_INFO {
  POINTER_INPUT_TYPE         pointerType;
  UINT32                     pointerId;
  UINT32                     frameId;
  POINTER_FLAGS              pointerFlags;
  HANDLE                     sourceDevice;
  HWND                       hwndTarget;
  POINT                      ptPixelLocation;
  POINT                      ptHimetricLocation;
  POINT                      ptPixelLocationRaw;
  POINT                      ptHimetricLocationRaw;
  DWORD                      dwTime;
  UINT32                     historyCount;
  INT32                      inputData;
  DWORD                      dwKeyStates;
  UINT64                     PerformanceCount;
  POINTER_BUTTON_CHANGE_TYPE ButtonChangeType;
} POINTER_INFO;

typedef enum tagTOUCH_FLAGS {
  TOUCH_FLAG_NONE = 0x00000000,
} TOUCH_FLAGS;

typedef enum tagTOUCH_MASK {
  TOUCH_MASK_NONE        = 0x00000000, // Default - none of the optional fields are valid
  TOUCH_MASK_CONTACTAREA = 0x00000001, // The rcContact field is valid
  TOUCH_MASK_ORIENTATION = 0x00000002, // The orientation field is valid
  TOUCH_MASK_PRESSURE    = 0x00000004, // The pressure field is valid
} TOUCH_MASK;

typedef struct _RECT {
  LONG left;
  LONG top;
  LONG right;
  LONG bottom;
} RECT, *PRECT;

typedef struct tagPOINTER_TOUCH_INFO {
    POINTER_INFO    pointerInfo;
    TOUCH_FLAGS     touchFlags;
    TOUCH_MASK      touchMask;
    RECT            rcContact;
    RECT            rcContactRaw;
    UINT32          orientation;
    UINT32          pressure;
} POINTER_TOUCH_INFO;

BOOL InitializeTouchInjection(
  UINT32 maxCount,
  DWORD  dwMode
);

BOOL InjectTouchInput(
  UINT32 count,
  const POINTER_TOUCH_INFO *contacts
);

#define TOUCH_FEEDBACK_DEFAULT 0x1
#define TOUCH_FEEDBACK_INDIRECT 0x2
#define TOUCH_FEEDBACK_NONE 0x3
""")

C = ffi.dlopen("User32.dll")

POINTER_FLAGS = {0: C.POINTER_FLAG_DOWN | C.POINTER_FLAG_INRANGE | C.POINTER_FLAG_INCONTACT, 
                 1: C.POINTER_FLAG_UPDATE | C.POINTER_FLAG_INRANGE | C.POINTER_FLAG_INCONTACT,
                 2: C.POINTER_FLAG_NONE,#C.POINTER_FLAG_UP,
                 3: C.POINTER_FLAG_UPDATE | C.POINTER_FLAG_INRANGE,
                 }

#Initialize Touch Injection
if (C.InitializeTouchInjection(4, C.TOUCH_FEEDBACK_INDIRECT)):
    print("Initialized Touch Injection")

ptPixelLocation = ffi.new("POINT *", {'x':0, 'y':0})

pointerInfo = ffi.new("POINTER_INFO *",
                        {'pointerType': C.PT_TOUCH,
                         'pointerId': 0,
                         'ptPixelLocation': ptPixelLocation[0],
                        })

rcContact = ffi.new("RECT *", {'left': 0,'top': 0, 'right': 0, 'bottom': 0})

touchInfo = ffi.new("POINTER_TOUCH_INFO *",
                    {'pointerInfo': pointerInfo[0],
                     'touchFlags': C.TOUCH_FLAG_NONE,
                     'touchMask': C.TOUCH_MASK_CONTACTAREA | C.TOUCH_MASK_ORIENTATION | C.TOUCH_MASK_PRESSURE,
                     'rcContact': rcContact[0],
                     'orientation': 90,
                     'pressure': 32000,
                    })



def makeTouch(x, y, figuerId, pointerFlag, fingerRadius=5):
    pointerInfo.pointerId = figuerId
    ptPixelLocation.x = x
    ptPixelLocation.y = y
    pointerInfo.ptPixelLocation = ptPixelLocation[0]
    touchInfo.pointerInfo = pointerInfo[0]
    
    rcContact.left = x - fingerRadius
    rcContact.top = y - fingerRadius
    rcContact.right = x + fingerRadius
    rcContact.bottom = y + fingerRadius

    touchInfo.rcContact = rcContact[0]
    
    touchInfo.pointerInfo.pointerFlags = pointerFlag

    return (C.InjectTouchInput(1, touchInfo) != 0)

