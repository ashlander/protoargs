#include <boost/filesystem.hpp>

#include "GTestGroups.h"

#include <Schema/simple.pa.h>

    using namespace boost;
    using namespace bsw;
    using namespace protoargs;

    class SimpleTests: public LogTest
    {
        public:
            SimpleTests() {}
            virtual ~SimpleTests() {}

        public:
            virtual void SetUp() override
            {
            }
    };

    TEST_F(SimpleTests, SimpleUsage)
    {
       const char* argv[] = {
          "program"
          ,"--help"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       simple::ProtoArgs arguments;
       auto config = std::shared_ptr<simple::protoargs>( arguments.parse(argv[0], argc, (char**)argv, true /*allow incomplete*/) );
       ASSERT_TRUE(config != nullptr);

       ASSERT_TRUE(config->help());

       const auto usage = arguments.usage(argv[0]);
       printMessage( usage );
       ASSERT_FALSE( usage.empty() );
    }

    TEST_F(SimpleTests, CheckAllPositive)
    {
       const char* argv[] = {
          "program"
          , "--count", "1"
          , "--configuration", "/tmp/conf"
          , "--flags", "true"
          , "--flags", "false"
          , "-c", "flags should be true and false"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       simple::ProtoArgs arguments;
       auto config = std::shared_ptr<simple::protoargs>( arguments.parse(argv[0], argc, (char**)argv) );
       ASSERT_TRUE(config != nullptr);

       ASSERT_EQ( 1u, config->count() );

       ASSERT_EQ( "/tmp/conf", config->configuration() );

       ASSERT_EQ( 2, config->flags_size() );
       ASSERT_TRUE( config->flags(0) );
       ASSERT_FALSE( config->flags(1) );

       ASSERT_EQ( "flags should be true and false", config->c() );
    }

    // positional will be skipped
    TEST_F(SimpleTests, CheckNoPositional)
    {
       const char* argv[] = {
          "program"
          , "--count", "1"
          , "--configuration", "/tmp/conf"
          , "--flags", "true"
          , "--flags", "false"
          , "-c", "flags should be true and false"
          , "positional_value"
          , "positional_value"
          , "positional_value"
          , "positional_value"
          , "positional_value"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       simple::ProtoArgs arguments;
       auto config = std::shared_ptr<simple::protoargs>( arguments.parse(argv[0], argc, (char**)argv) );
       ASSERT_TRUE(config != nullptr);

       ASSERT_EQ( 1u, config->count() );

       ASSERT_EQ( "/tmp/conf", config->configuration() );

       ASSERT_EQ( 2, config->flags_size() );
       ASSERT_TRUE( config->flags(0) );
       ASSERT_FALSE( config->flags(1) );

       ASSERT_EQ( "flags should be true and false", config->c() );
    }

    TEST_F(SimpleTests, CheckWrongType)
    {
       const char* argv[] = {
          "program"
          , "--count", "stringnotdigit"
          , "--configuration", "/tmp/conf"
          , "--flags", "true"
          , "--flags", "false"
          , "-c", "flags should be true and false"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       simple::ProtoArgs arguments;
       auto config = std::shared_ptr<simple::protoargs>( arguments.parse(argv[0], argc, (char**)argv) );
       ASSERT_TRUE(config == nullptr);
    }

