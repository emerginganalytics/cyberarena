#include<stdio.h>
#include<string.h>
#include<Windows.h>

int main(int argc, char *argv[]){
	
    if(IsDebuggerPresent())
	{
		MessageBox(0,"Please stop using the debugger to run the program.","Debugger detected!",0);
		return 0;
	}
	
    if(argc==2){
		printf("Enter a valid license key: %s\n", argv[1]);
		int sum =0;
		for(int i = 0; i < strlen(argv[1]); i++){
			sum+= (int)argv[1][i];
		}
		if(sum==1500){
			printf("Access Granted!\n");
		}else{
			printf("Access denied!\n");
		}
	}else{
		printf("Usage: <key>\n");
	}
	
	return 0;
}
