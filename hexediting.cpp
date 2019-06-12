/*

Author: Ryan Ronquillo
Date: 6/11/2019

*/
#include <iostream>
#include <cstdlib>

using namespace std;

void keyPuzzle(){
    int value = 7500;
    cout << "If you want the flag, you need to lower the value for the current number to 250!\n";
    cout << "The current value is: " << value << "\n";

    if(value == 250){
        cout << "54 68 65 20 66 6c 61 67 20 69 73 3a 20 7b 75 61 6c 72 5f 68 65 78 65 64 69 74 69 6e 67 5f 63 68 61 6c 6c 65 6e 67 65 7d";
    }
}

int main() {

    int attempts = 3;
    string password;

    while(password != "iamthepassword"){
        cout << "Enter a password: ";
        cin >> password;

    if (password != "iamthepassword"){
        cout << "Incorrect password!\n";
        attempts--;
        if(attempts == 0){
            exit(0);
        }
    }
    else{
        system("cls");
        cout << "Correct password!\n";
        keyPuzzle();
    }

    }
    return 0;
}
