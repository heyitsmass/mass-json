#include <iostream> 
#include <vector> 
#include <unordered_map>  
#include <regex>  

using namespace std; 
template<typename T> 
struct Token{ 
  Token(string k, T v, bool f=false): kind(k), value(v), flag(f) {};

  public: 
    string kind; 
    T value; 
    bool flag; 
};

template<typename T> 
struct Pair{ 
  Pair(string k, Token<T> t): key(k), token(t) {}; 

  public: 
    string key; 
    Token<T> token; 
}; 

template <typename T> 
struct Data{ 
  Data(T& d): data(d){};
  public: 
    T data; 
}; 


class _json_{ 
  string text;
  public:

    _json_(string t){ 
      text = t; 
     // Data ret = this -> scan(); 
    } 
}; 

/* 
_json_& load(string text){ 
  return _json_(text);
}
*/ 


string getKey(int index=0){ 
  string key = ""; 
  string text = "\"str,\\ing\""; 

  regex tok_regex = regex("\"(?:(?:(?!\\\\)[^\"])*(?:\\\\[\bfnrt\"]|\\\\u[0-9a-fA-F]{4}|\\\\)?)+?\"\\s*");

  smatch sm; 
  auto match = regex_match(text, sm, tok_regex);
  cout << match << endl;  
  cout << sm[0] << endl;
  
  return key; 
}

int main(int argv, char** argc){

  unordered_map<string, string> tokens = { 
    {"string" , "\"(?:(?:(?!\\\\)[^\"])*(?:\\\\[\bfnrt\"]|\\\\u[0-9a-fA-F]{4}|\\\\)?)+?\""},
    {"number" , "[-]?\\d+(?:[.]?\\d+)?(?:[Ee]?[-+]?\\d+)?"},
    {"boolean" , "true|false"},
    {"null" , "null"},
    {"ws" , "\\s*"},
    {"newline" , "\n"},
    {"colon" , ":"},
    {"comma" , ","},
    {"dict_start", "\\{"},
    {"dict_end", "\\}"},
    {"arr_start", "\\["},
    {"arr_end", "\\]"},
    {"mismatch" , "."}
  }; 


  auto key = getKey(); 

  cout << key << endl; 

  /* Styles 

  Data< vector<string> > -> array 
  Data< unordered_map<string, type2> > -> object 

  */ 



  return 0; 
} 