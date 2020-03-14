#pragma once
#include <string.h>
#include "test.h"


#define LOGPRIORITY_MAX_LEN 12
#define LOGPRIORITY_PARSER(n, buf) do {\
        switch(n) {\
        case LOG_UNKNOWN:\
                strcpy(buf, "LOG_UNKNOWN");\
                break;\
        case LOG_DEFAULT:\
                strcpy(buf, "LOG_DEFAULT");\
                break;\
        case LOG_VERBOSE:\
                strcpy(buf, "LOG_VERBOSE");\
                break;\
        case LOG_DEBUG:\
                strcpy(buf, "LOG_DEBUG");\
                break;\
        case LOG_INFO:\
                strcpy(buf, "LOG_INFO");\
                break;\
        case LOG_WARN:\
                strcpy(buf, "LOG_WARN");\
                break;\
        case LOG_ERROR:\
                strcpy(buf, "LOG_ERROR");\
                break;\
        default:\
                strcpy(buf, "Unknown");\
                break;\
        }\
    } while (0);


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


