// HelloWorld.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <fstream>

using namespace  std; 


int main()
{
    cout << "Hello World!\n";

    ifstream ifs; 


    ifs.open("20240701_example_file_v2.xlsx - Sheet1.tsv");
    if (ifs.is_open() == false) // open the read file failed
    {
        cout << "ERROR! failed to read the file!" << endl; 
        return 1; 
    }

    // Dump the contents of the file to cout
    cout << ifs.rdbuf() << endl; 
    ifs.close();
    return 0; 

}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
