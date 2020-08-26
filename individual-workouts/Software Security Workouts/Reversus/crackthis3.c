#include<stdio.h>
#include<string.h>

int main(int argc, char *argv[]){
    if(argc==2){
		printf("Enter a valid license key: %s\n", argv[1]);
		int sum =0;
		for(int i = 0; i < strlen(argv[1]); i++){
			sum+= (int)argv[1][i];
		}
		if(sum==882){
			printf("Access Granted!\n");
		}else{
			printf("Access denied!\n");
		}
	}else{
		printf("Usage: <key>\n");
	}
	
	return 0;
}
	