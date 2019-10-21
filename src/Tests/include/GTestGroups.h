#include <gtest/gtest.h>
#include <boost/filesystem.hpp>

//#include "ProtoconfConfig.h"

#include <Logger/log.h>
#include <Common/macro.h>

class LogTest : public ::testing::Test
{
    public:
        LogTest()
            : _path(std::string( STRINGIFYVALUE(Protoconf_PROJECT_PATH) ) + "/Tests/playground/")
        {}

        virtual ~LogTest() {}

    public:
        virtual void SetUp()
        {
            FILELog::ReportingLevel() = logDEBUG;
        }

        virtual void printMessage(const std::string& message)
        {
            std::string messageStart("[      INF ] ");
            std::string lineStart("[          ] ");
            std::string output = message;
            size_t pos = output.find("\n");
            while (pos != std::string::npos)
            {
               output.insert(pos+1, lineStart);
               pos = output.find("\n", pos+1);
            }//while
            std::cerr << messageStart + output << std::endl;
        }

        virtual std::string getTestFilesPath(const std::string& testDir, const std::string& testFile = std::string("")) const
        {
            const std::string section("generated");
            boost::filesystem::path path("/tmp/smallstep");
            boost::filesystem::create_directories(path / testDir / section );
            return (path / testDir / section / testFile).normalize().string();
        }

        virtual std::string getTestBinPath(const std::string& testDir, const std::string& testFile = std::string("")) const
        {
            return getTestPath(testDir, "bin", testFile);
        }

        virtual std::string getTestRunPath(const std::string& testDir, const std::string& testFile = std::string("")) const
        {
            return getTestPath(testDir, "run", testFile);
        }

    protected:
        virtual std::string getTestPath(const std::string& testDir, const std::string& section, const std::string& testFile = std::string("")) const
        {
            return (_path / testDir / section / testFile).normalize().string();
        }

    protected:
        boost::filesystem::path _path;

        //virtual void TearDown() { }
};// LogTest

