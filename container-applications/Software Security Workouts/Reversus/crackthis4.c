#include<stdio.h>
#include<string.h>
#include<Windows.h>

int main(int argc, char** argv){
    unsigned char s[] = 
    {
        0x73, 0x65, 0x63, 0x72, 0x65, 0x74, 0x61, 0x75, 
        0x74, 0x68, 0x63, 0x6f, 0x64, 0x65, 0x0
    };

    for (unsigned int m = 0; m < sizeof(s); ++m)
    {
        unsigned char c = s[m];
        s[m] = c;
    }
	if(argc==2){
		printf("Enter secret authentication code: %s\n", argv[1]);
	    if(strcmp(s, argv[1]) == 0)
	    {
		    printf("Access granted!");
	    }else{
		    printf("Access denied!");
	    }
	}else{
		printf("Usage: <key>\n");

	    return 0;
	}
}
