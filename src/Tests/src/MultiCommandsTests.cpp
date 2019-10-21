#include <boost/filesystem.hpp>

#include "GTestGroups.h"

#include <Schema/multy_command.pa.h>
#include <Schema/multy_command_create.pa.h>
#include <Schema/multy_command_copy.pa.h>

    using namespace boost;
    using namespace bsw;
    using namespace protoargs;

    class MultiCommandsTests: public LogTest
    {
        public:
            MultiCommandsTests() {}
            virtual ~MultiCommandsTests() {}

        public:
            virtual void SetUp() override
            {
            }
    };

    TEST_F(MultiCommandsTests, MultiCommandsUsage)
    {
       const char* argv[] = {
          "program"
          ,"-h"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       main::ProtoArgs arguments;
       auto config = std::shared_ptr<main::protoargs>( arguments.parse(argv[0], argc, (char**)argv, true /*allow incomplete*/) );
       ASSERT_TRUE(config != nullptr);

       ASSERT_TRUE(config->help());

       const auto usage = arguments.usage(argv[0]);
       printMessage( usage );
       ASSERT_FALSE( usage.empty() );
    }

    TEST_F(MultiCommandsTests, MultiCommandsCreateUsage)
    {
       const char* argv[] = {
          "program", "create"
          ,"-h"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       std::string program(argv[0]);
       std::string command;

       { // check main args
          main::ProtoArgs arguments;
          auto config = std::shared_ptr<main::protoargs>( arguments.parse(program, argc, (char**)argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_EQ("create", config->command());
          command = config->command();
       }

       { // check create args
          program += " " + command;

          main::create::ProtoArgs arguments;
          auto config = std::shared_ptr<main::create::protoargs>( arguments.parse(program, argc, (char**)argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_TRUE(config->help());

          const auto usage = arguments.usage(program);
          printMessage( usage );
          ASSERT_FALSE( usage.empty() );
       }
    }

    TEST_F(MultiCommandsTests, CheckAllPositiveCreate)
    {
       const char* argv[] = {
          "program", "create"
          ,"-s", "2048"
          , "/tmp/tmp.file"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       std::string program(argv[0]);
       std::string command;

       { // check main args
          main::ProtoArgs arguments;
          auto config = std::shared_ptr<main::protoargs>( arguments.parse(program, 2 /*need only 2 args to detect command*/, (char**)argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_EQ("create", config->command());
          command = config->command();
       }

       { // check create args
          program += " " + command;

          main::create::ProtoArgs arguments;

          auto filtered = arguments.exclude(argc, (char**)argv, { 2, 50 }); // 2nd position with command, 50 - just ignored, no arg with 50th position

          auto config = std::shared_ptr<main::create::protoargs>( arguments.parse(program, filtered.argc, filtered.argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_EQ(2048u, config->size());
          ASSERT_EQ("/tmp/tmp.file", config->path());
       }
    }


    TEST_F(MultiCommandsTests, MultiCommandsCopyUsage)
    {
       const char* argv[] = {
          "program", "copy"
          ,"-h"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       std::string program(argv[0]);
       std::string command;

       { // check main args
          main::ProtoArgs arguments;
          auto config = std::shared_ptr<main::protoargs>( arguments.parse(program, argc, (char**)argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_EQ("copy", config->command());
          command = config->command();
       }

       { // check create args
          program += " " + command;

          main::copy::ProtoArgs arguments;
          auto config = std::shared_ptr<main::copy::protoargs>( arguments.parse(program, argc, (char**)argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_TRUE(config->help());

          const auto usage = arguments.usage(program);
          printMessage( usage );
          ASSERT_FALSE( usage.empty() );
       }
    }

    TEST_F(MultiCommandsTests, CheckAllPositiveCopy)
    {
       const char* argv[] = {
          "program", "copy"
          ,"-r"
          , "/tmp/tmp.file.src"
          , "/tmp/tmp.file.dst"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       std::string program(argv[0]);
       std::string command;

       { // check main args
          main::ProtoArgs arguments;

          auto config = std::shared_ptr<main::protoargs>( arguments.parse(program, 2 /*need only 2 args to detect command*/, (char**)argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_EQ("copy", config->command());
          command = config->command();
       }

       { // check create args
          program += " " + command;

          main::copy::ProtoArgs arguments;

          auto filtered = arguments.exclude(argc, (char**)argv, { 2, 50 }); // 2nd position with command, 50 - just ignored, no arg with 50th position

          auto config = std::shared_ptr<main::copy::protoargs>( arguments.parse(program, filtered.argc, filtered.argv, true /*allow incomplete*/) );
          ASSERT_TRUE(config != nullptr);

          ASSERT_TRUE(config->recursive());
          ASSERT_EQ("/tmp/tmp.file.src", config->src());
          ASSERT_EQ("/tmp/tmp.file.dst", config->dst());
       }
    }
