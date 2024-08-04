import inlinecpp
mymodule = inlinecpp.createLibrary(
    name="cpp_string_library",
    includes="#include <UT/UT_String.h>",
    function_sources=[
"""
 bool matchesPattern(const char *str, const char *pattern)
{
    return UT_String(str).multiMatch(pattern);
}
"""])
string = "one"
for pattern in "o*", "x*", "^o*":
    print (repr(string), "matches", repr(pattern), ":",)
    print (mymodule.matchesPattern(string, pattern))