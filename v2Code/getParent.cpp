
void getParent(){
for (int i=0; i<jointsPath.size();++i) {
            std::string path = jointsPath[i].GetString();
            std::string name = jointNames[i].GetString();
            std::string parentName;

            std::vector<std::string> pathTokens;
            size_t start = 0;
            size_t end = path.find('/');
            while (end != std::string::npos) {
                pathTokens.push_back(path.substr(start, end - start));
                start = end + 1;
                end = path.find('/', start);
            }
            pathTokens.push_back(path.substr(start));

            // Find the index of the name
            size_t nameIndex = std::find(pathTokens.begin(), pathTokens.end(), name) - pathTokens.begin();

            if (nameIndex > 0 && nameIndex < pathTokens.size()) {
                parentName = pathTokens[nameIndex - 1];
                std::cout << "Parent name: " << parentName << std::endl;
            } else {
                std::cout << "Parent name not found." << std::endl;
            }

            jointsParent.push_back(parentName);
        }

        for(const auto& string : jointsParent){
            std::cout<<string<<"\n";
        }
}
