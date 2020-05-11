#include <stdio.h>

#include "test.h"
#include "result.h"

int main(void)
{
    printf("LOG_VERBOSE=%s\n", logpriority_parser(LOG_VERBOSE));
    
    printf("LOG_ID_MIN=%s    (expected LOG_ID_MIN_OR_MAIN)\n", log_id_parser(LOG_ID_MIN));

    char buf[DF_MAX_LEN] = { 0 };
    DF_PARSER(DF_BIND_NOW, buf);
    printf("DF_BIND_NOW=%s\n", buf);

    char buf2[DF_1_MAX_LEN] = { 0 };
    DF_1_PARSER(DF_1_INITFIRST, buf2);
    printf("DF_1_INITFIRST=%s\n", buf2);

}
