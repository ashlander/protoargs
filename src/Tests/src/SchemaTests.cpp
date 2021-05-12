#include <boost/filesystem.hpp>

#include "GTestGroups.h"

#include <Schema/schema.pa.h>

    using namespace boost;
    using namespace bsw;
    using namespace protoargs;

    class SchemaTests: public LogTest
    {
        public:
            SchemaTests() {}
            virtual ~SchemaTests() {}

        public:
            virtual void SetUp() override
            {
            }
    };

    TEST_F(SchemaTests, SchemaUsage)
    {
       const char* argv[] = {
          "program"
          ,"--help"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv, true /*allow incomplete*/) );
       ASSERT_TRUE(config != nullptr);

       ASSERT_TRUE(config->printhelp());

       const auto usage = arguments.usage("program");
       printMessage( usage );
       ASSERT_FALSE( usage.empty() );
    }

    TEST_F(SchemaTests, CxxoptsConnectsShortAndLongArgsTogether)
    {
       const char* argv[] = {
          "program"
          , "-e", "valueE"
          , "--a-long-param", "somevalue" // inside pa.cc only '-a' is analized
          , "50" // paramG
          , "0" // bool paramG
          , "0.5" // PARAM-FLOAT
          , "0.7" // PARAM-DOUBLE
          , "pos1", "pos2", "pos3"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv) );
       ASSERT_TRUE(config != nullptr);

       ASSERT_TRUE( config->has_parama() );
    }

    TEST_F(SchemaTests, SchemaPositiveShort)
    {
       const char* argv[] = {
          "program"
          ,"-e", "valueE"
          , "50" // paramG
          , "0" // bool paramG
          , "0.5" // PARAM-FLOAT
          , "0.7" // PARAM-DOUBLE
          , "pos1", "pos2", "pos3"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv) );
       ASSERT_TRUE(config != nullptr);

       // check defaults
       ASSERT_FALSE( config->has_parama() );
       ASSERT_EQ( "// tricky default value", config->parama() );

       ASSERT_FALSE( config->has_paramb() );
       ASSERT_EQ( 10u, config->paramb() );

       ASSERT_FALSE( config->has_paramc() );
       ASSERT_EQ( 0, config->paramc() );

       ASSERT_FALSE( config->has_paramd() );
       ASSERT_EQ( 0.0f, config->paramd() );

       ASSERT_TRUE( config->has_parame() );
       ASSERT_EQ( "valueE", config->parame() );

       ASSERT_EQ( 0, config->paramf_size() );

       ASSERT_FALSE( config->has_param_i() );
       ASSERT_TRUE( config->param_i() );

       ASSERT_FALSE( config->has_param_j() );
       ASSERT_FALSE( config->param_j() );
    }

    TEST_F(SchemaTests, SchemaPositiveAll)
    {
       const char* argv[] = {
          "program"
          ,"-e", "valueE"
          ,"--a-long-param", "somevalue"
          ,"--b-long-param", "4"
          ,"-c", "555"
          ,"--d-long-param", "555.5"
          ,"-f", "1"
          ,"-f", "2"
          ,"-f", "3"
          ,"-i"
          ,"--j-long"
          , "50" // paramG
          , "0" // bool paramG
          , "0.5" // PARAM-FLOAT
          , "0.7" // PARAM-DOUBLE
          , "pos1", "pos2", "pos3" // paramH
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv) );
       ASSERT_TRUE(config != nullptr);

       ASSERT_TRUE( config->has_parama() );
       ASSERT_EQ( "somevalue", config->parama() );

       ASSERT_TRUE( config->has_paramb() );
       ASSERT_EQ( 4u, config->paramb() );

       ASSERT_TRUE( config->has_paramc() );
       ASSERT_EQ( 555, config->paramc() );

       ASSERT_TRUE( config->has_paramd() );
       ASSERT_EQ( 555.5f, config->paramd() );

       ASSERT_TRUE( config->has_parame() );
       ASSERT_EQ( "valueE", config->parame() );

       ASSERT_EQ( 3, config->paramf_size() );

       ASSERT_TRUE( config->has_param_i() );
       ASSERT_TRUE( config->param_i() );

       ASSERT_TRUE( config->has_param_j() );
       ASSERT_TRUE( config->param_j() );
    }

   /**
    * @brief Required means required
    */
    TEST_F(SchemaTests, MissingRequired)
    {
       const char* argv[] = {
          "program"
          , "50" // paramG
          , "0" // bool paramG
          , "pos1", "pos2", "pos3"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv) );
       ASSERT_TRUE(config == nullptr);
    }

   /**
    * @brief Repeated positional args should ba at least one set
    */
    TEST_F(SchemaTests, MissingRepeatedPositional)
    {
       const char* argv[] = {
          "program"
          ,"-e", "valueE"
          , "50" // paramG
          , "0" // bool paramG
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv) );
       ASSERT_TRUE(config == nullptr);
    }

   /**
    * @brief Wrong type for positional arg
    */
    TEST_F(SchemaTests, PositionalWrongType)
    {
       const char* argv[] = {
          "program"
          ,"-e", "valueE"
          , "pos1", "pos2", "pos3"
       };
       int argc = sizeof(argv)/sizeof(argv[0]);
       schema::ProtoArgs arguments;
       auto config = std::shared_ptr<schema::protoargs>( arguments.parse("program", argc, (char**)argv) );
       ASSERT_TRUE(config == nullptr);
    }

