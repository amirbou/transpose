# Transpose

Transpose is a Python package that helps you write C code. 

Given a C header file, Transpose will take all the enums and macros that can be resolved to an numeric value and create a new header file.
In the generated header file you will find macros that take a numeric value and return its name.
Transpose will try to combine as many macros in the original file to a single value parser

## Installation
clone the repository:
```
git clone https://github.com/amirbou/transpose.git
```
and use pip:
```
pip3 install ./transpose
```

## Usage
```
$ transpose --help
usage: transpose [-h] [-D macro[=defn]] [-r] [--parse-std] [--compiler COMPILER] [-I dir] [--max-headers MAX_HEADERS] [-f,--force] in_file out_file

Create macros to reverse enums and defines from header file

positional arguments:
  in_file               input file
  out_file              output file.

optional arguments:
  -h, --help            show this help message and exit
  -D macro[=defn]       pass macros, as in gcc, for the preproceccor (i.e -D DEBUG)
  -r                    recursively transpose included headers, by default, only #include "header.h" are parsed (not <header.h>)
  --parse-std           when -r is given parse <> includes as well
  --compiler COMPILER   when parse-std is given, use the same default include directories as the provided compiler
  -I dir                add include directories to search when recursively transposing headers
  --max-headers MAX_HEADERS
                        maximum number of headers to parse in recursion mode (20 by default)
  -f,--force            overwrite existing out_path


```

# Features

- Parsing complicated definitions such as:
    ```c
    #define __NR_SYSCALL_BASE 0
    #define __NR_ptrace (__NR_SYSCALL_BASE + 26)
    ```
    and even some diabolical ones such as:
    ```c
    #define BASE 0
    #define TWO (ONE + 1)
    #define ONE (BASE + 1)
    ```
    To ensure macros with same value are handled correctly

- Recursivly parsing ```#include``` statements in the given header file (```-r```)
- Manually passing macros with ```-D DEBUG=1 -D _GNU_SOURCE```
- Adding include directories with ```-I dir1 -I dir2```
- Parsing standard headers with ```--parse-std```
- Specifying a compiler for using its search path when searching for headers with ```--compiler /bin/clang```
- If [argcomplete](https://pypi.org/project/argcomplete/) is installed, you can enjoy autocompletion in bash by using ```activate-global-python-argcomplete``` or adding ```eval "$(register-python-argcomplete transpose)"``` to your ```bash.rc```


## Examples
Given the header file ```log.h```
```c 
// log.h
typedef enum log_id {
  LOG_ID_MIN = 0,
  LOG_ID_MAIN = 0,
  LOG_ID_RADIO = 1,
  LOG_ID_EVENTS = 2,
  LOG_ID_SYSTEM = 3,
  LOG_ID_CRASH = 4,
  LOG_ID_STATS = 5,
  LOG_ID_SECURITY = 6,
  LOG_ID_KERNEL = 7,

  LOG_ID_MAX
} log_id_t;
```

Running: 
```shell
$ transpose log.h example.h
```
```c
// example.h

#pragma once
#include <string.h>
#include "log.h"

#define LOG_ID_MAX_LEN 19
#define LOG_ID_PARSER(n, buf) do {\
    switch(n) {\
    case LOG_ID_MIN:\
            strcpy(buf, "LOG_ID_MIN_OR_MAIN");\
            break;\
    case LOG_ID_RADIO:\
            strcpy(buf, "LOG_ID_RADIO");\
            break;\
    case LOG_ID_EVENTS:\
            strcpy(buf, "LOG_ID_EVENTS");\
            break;\
    case LOG_ID_SYSTEM:\
            strcpy(buf, "LOG_ID_SYSTEM");\
            break;\
    case LOG_ID_CRASH:\
            strcpy(buf, "LOG_ID_CRASH");\
            break;\
    case LOG_ID_STATS:\
            strcpy(buf, "LOG_ID_STATS");\
            break;\
    case LOG_ID_SECURITY:\
            strcpy(buf, "LOG_ID_SECURITY");\
            break;\
    case LOG_ID_KERNEL:\
            strcpy(buf, "LOG_ID_KERNEL");\
            break;\
    case LOG_ID_MAX:\
            strcpy(buf, "LOG_ID_MAX");\
            break;\
    default:\
            strcpy(buf, "Unknown");\
            break;\
    }\
} while (0);
```

As you can see, when presentent with confilicting values, Transpose will use the longest shared prefix (of words delimeted by _ ) and add an _OR_ between the remaining words of each name to generate the result.

If the header file uses macros, Transpose will work hard to find all the shared prefixes, and generate the least amount of parsers

For example:
```c
// elf.h

#define DF_ORIGIN     0x00000001
#define DF_SYMBOLIC   0x00000002
#define DF_TEXTREL    0x00000004
#define DF_BIND_NOW   0x00000008
#define DF_STATIC_TLS 0x00000010       
                    
#define DF_1_NOW        0x00000001 // has the same value as DF_ORIGIN, so two parsers will be created
#define DF_1_GLOBAL     0x00000002       
#define DF_1_GROUP      0x00000004
#define DF_1_NODELETE   0x00000008
#define DF_1_LOADFLTR   0x00000010      
#define DF_1_INITFIRST  0x00000020
```

Running 
```shell
$ transpose elf.h example2.h
```
```c
#pragma once
#include <string.h>
#include "elf.h"

#define DF_MAX_LEN 14
#define DF_PARSER(n, buf) do {\
    switch(n) {\
    case DF_ORIGIN:\
            strcpy(buf, "DF_ORIGIN");\
            break;\
    case DF_SYMBOLIC:\
            strcpy(buf, "DF_SYMBOLIC");\
            break;\
    case DF_TEXTREL:\
            strcpy(buf, "DF_TEXTREL");\
            break;\
    case DF_BIND_NOW:\
            strcpy(buf, "DF_BIND_NOW");\
            break;\
    case DF_STATIC_TLS:\
            strcpy(buf, "DF_STATIC_TLS");\
            break;\
    default:\
            strcpy(buf, "Unknown");\
            break;\
    }\
} while (0);


#define DF_1_MAX_LEN 15
#define DF_1_PARSER(n, buf) do {\
    switch(n) {\
    case DF_1_NOW:\
            strcpy(buf, "DF_1_NOW");\
            break;\
    case DF_1_GLOBAL:\
            strcpy(buf, "DF_1_GLOBAL");\
            break;\
    case DF_1_GROUP:\
            strcpy(buf, "DF_1_GROUP");\
            break;\
    case DF_1_NODELETE:\
            strcpy(buf, "DF_1_NODELETE");\
            break;\
    case DF_1_LOADFLTR:\
            strcpy(buf, "DF_1_LOADFLTR");\
            break;\
    case DF_1_INITFIRST:\
            strcpy(buf, "DF_1_INITFIRST");\
            break;\
    default:\
            strcpy(buf, "Unknown");\
            break;\
    }\
} while (0);
```

If the header file contains an ```#ifdef A``` statement, transpose will ignore it unless A is defined (either with -D or in a previously included header in recursive mode):
```c
// one.h
#ifdef TEST
#define ONE '1'
#endif
```
Running ```transpose one.h example3_bad.h``` will result in:
```c
// example3_bad.h
#pragma once
#include <string.h>
#include "one.h"
```
But Running ```transpose one.h example3_good.h -D TEST``` would give us:
```c
// example3_good.h

#pragma once
#include <string.h>
#include "one.h"

#define _DEFAULT_MAX_LEN 8
#define _DEFAULT_PARSER(n, buf) do {\
    switch(n) {\
    case ONE:\
            strcpy(buf, "ONE");\
            break;\
    default:\
            strcpy(buf, "Unknown");\
            break;\
    }\
} while (0);
```

Lastly, if some macros are dependent on an included header, such as:
```c
// common.h
#define BASE 1000
```
```c
// id.h
#include "common.h"
#define SHELL (BASE + 1000)
```

Running ```transpose id.h example4.h -r``` would yield:
```c
#pragma once
#include <string.h>
#include "id.h"

#define _DEFAULT_MAX_LEN 8
#define _DEFAULT_PARSER(n, buf) do {\
    switch(n) {\
    case BASE:\
            strcpy(buf, "BASE");\
            break;\
    case SHELL:\
            strcpy(buf, "SHELL");\
            break;\
    default:\
            strcpy(buf, "Unknown");\
            break;\
    }\
} while (0);
```
