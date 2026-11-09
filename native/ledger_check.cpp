// CF-0 native migration: read-only JSONL shape diagnostic. C++17.
// NOT a JSON parser, hash verifier, or task verifier.
#include <fstream>
#include <iostream>
#include <string>
#include <cctype>
static bool shape(const std::string& s) {
    bool quoted=false, escaped=false, started=false, ended=false;
    int objects=0, arrays=0;
    for (unsigned char ch : s) {
        if (quoted) {
            if (escaped) escaped=false;
            else if (ch=='\\') escaped=true;
            else if (ch=='"') quoted=false;
            continue;
        }
        if (ch=='"') { quoted=true; continue; }
        if (std::isspace(ch) && !started) continue;
        if (!started) { if (ch!='{') return false; started=true; }
        if (ended && !std::isspace(ch)) return false;
        if (ch=='{') ++objects;
        if (ch=='}') {
            if (--objects<0) return false;
            if (objects==0 && arrays==0) ended=true;
        }
        if (ch=='[') ++arrays;
        if (ch==']' && --arrays<0) return false;
    }
    return started && ended && !quoted && objects==0 && arrays==0;
}
int main(int argc, char** argv) {
    if (argc!=2) { std::cerr<<"Usage: cf-ledger-shape PATH_TO_JSONL\n"; return 2; }
    std::ifstream in(argv[1]);
    if (!in) { std::cerr<<"Cannot open file\n"; return 2; }
    std::string line;
    std::size_t total=0, suspicious=0;
    while (std::getline(in,line)) {
        ++total;
        if (!shape(line)) {
            ++suspicious;
            std::cerr<<"Suspicious structure on line "<<total<<'\n';
        }
    }
    if (in.bad()) { std::cerr<<"Read error\n"; return 2; }
    std::cout<<"Lines: "<<total<<", suspicious: "<<suspicious<<'\n';
    std::cout<<"Not full JSON validation or cryptographic verification.\n";
    return suspicious ? 1 : 0;
}
