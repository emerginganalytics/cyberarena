#include <iostream>
#include <string>
#include <vector>
#include <math.h>
#include <fstream>

std::string vec2string(std::vector<int>);
std::vector<int>string2Vec(std::string);
std::vector<int>encryptor(std::vector<int>);
void writeString(std::string);

int main(int argc, const char * argv[])
{

    std::string a = argv[1];
    writeString(vec2string(encryptor(string2Vec(a))));
    
    return 0;
}

std::vector<int>string2Vec(std::string x)
{
    std::vector<int>a;
    for(int i = 0; i < x.length(); ++i)
    {
        a.push_back(x.at(i));
    }
    
    return a;
}

std::string vec2string(std::vector<int> x)
{
    std::string y = "";
    
    for(int i = 0; i < x.size(); ++i)
    {
        if(i < x.size() - 1)
            y += std::to_string(x.at(i)) + "-";
        else
            y += std::to_string(x.at(i));
    }
    
    return y;
}

std::vector<int>encryptor(std::vector<int> x)
{
    for(int i = 0; i < x.size(); ++i)
    {
        x.at(i) *= x.size();
    }
    
    return x;
}

void writeString(std::string x)
{
    std::ofstream textFile;
    textFile.open("Encoded_Flag.txt");
    textFile << x << "\n";
    textFile.close();
}
