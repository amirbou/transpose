#include <stdio.h>

#include "test.h"
#include "result.h"

int main(void)
{
    printf("LOG_VERBOSE=%s\n", logpriority_parser(LOG_VERBOSE));
    
    printf("LOG_ID_MIN=%s    (expected LOG_ID_MIN_OR_MAIN)\n", log_id_parser(LOG_ID_MIN));

    printf("DF_BIND_NOW=%s\n",df_parser(DF_BIND_NOW));

    printf("DF_1_INITFIRST=%s\n", df_1_parser(DF_1_INITFIRST));

    return 0;
}
