import logging

# GLOBAL DEFS ###################################3

#class Protoargs:
pa_main = "protoargs"
pa_links = "protoargs_links"

#class ProtoDirectives:
pd_package = "package"
pd_message = "message"
pd_enum = "enum"
pd_field = "field"
pd_end = "}"

#class ProtoFields:
pf_required = "required"
pf_optional = "optional"
pf_repeated = "repeated"

# END GLOBALS ###################################3


class ProtoToken:
    directive = ""
    field = ""
    type = ""
    name= ""
    position = ""
    value = ""
    description = ""

    def valid(self):
        return bool(self.directive)

    def __repr__(self):
        return "(" + self.directive + "," + self.field + "," + self.type + "," + self.name + "," + self.position + "," + self.value + ",'" + self.description + "')"


class Tokenizer:

    __tokens = [] # result of lines parsing

    def getTokens(self):
        return self.__tokens

    # Exclude directive instances
    def excludeDirective(self, directive, name):
        if directive == pd_message or directive == pd_enum: # no other directive possible
            tokens = self.__tokens
            filteredTokens = []
            skip = False;
            for token in tokens:
                if not skip:
                    #print "[TST] " + str(token) + " Check: " + directive + ", " + name
                    if directive == token.directive and name == token.name:
                        skip = True # skipping, starting from current line
                    #elif directive != token.directive:
                    else:
                        filteredTokens.append(token) # let the token stay
                elif token.directive == pd_end:
                    skip = False
            self.__tokens = filteredTokens
        return self

    # Exclude unused structures from tokens
    def excludeUnused(self):
        tokens = self.__tokens
        unusedTokens = []
        for token in tokens:
            if token.directive == pd_enum:
                logging.warn("enums are not supported, exclude '" + token.name + "'")
                unusedTokens.apend(token)
            elif token.directive == pd_message:
                if token.name.find(pa_main) == -1 and token.name.find(pa_links) == -1: # Check for predefined messages
                    logging.warn("other messages are not needed, exclude '" + token.name + "'")
                    unusedTokens.append(token)

        # removing structures
        for unused in unusedTokens:
            self.excludeDirective(unused.directive, unused.name)

        return self

    def getToken(self, directive, name):
        found = False
        tokens = self.__tokens
        result = ProtoToken()
        for token in tokens:
            if token.directive == directive and token.name == name:
                result = token
                break
        return result

    def check(self): # Add more checks
        # check if needed messages present
        foundProtoargs = self.getToken(pd_message, pa_main).valid()
        foundProtoargsLinks = self.getToken(pd_message, pa_links).valid()

        logging.debug("-----------------------------------------------------")
        logging.debug(pa_main + " message: " + str(foundProtoargs))
        logging.debug(pa_links +" message: " + str(foundProtoargsLinks))
        logging.debug("-----------------------------------------------------")

        return foundProtoargs

    # parse field line and return token for it
    def createFieldToken(self, line):
        line = line.replace("\t"," ");
        chunks = line.split(" ")

        token = ProtoToken()
        token.directive = pd_field
        token.field = chunks[0].strip()
        token.type = chunks[1].strip()
        token.name = chunks[2].strip()
        token.position = chunks[4].replace(";","").strip()

        # discover default value
        nocomment = self.__removeComment(line)
        if nocomment.find("]") != -1:
            token.value = nocomment \
                    .split("]")[0] \
                    .split("[")[1] \
                    .split("=")[1] \
                    .strip()
            if token.value[0] == '"': # remove " from string
                token.value = token.value[1:len(token.value)-1]

        # comment on the same line is our description
        token.description = line.split(";")[1].strip()
        token.description = token.description[2:len(token.description)].strip() # remove starting //

        return token

    def createPackageToken(self, line):
        line = self.__removeComment(line)
        token = ProtoToken()
        token.directive = pd_package
        token.name = line \
                .replace(";","") \
                .replace(pd_package,"") \
                .strip()
        return token

    def __createMessageToken(self, line):
        line = self.__removeComment(line)
        token = ProtoToken()
        token.directive = pd_message
        token.name = line \
                .replace(";","") \
                .replace(pd_message,"") \
                .strip()
        return token

    def __createEndToken(self, line):
        token = ProtoToken()
        token.directive = pd_end
        return token

    def __removeComment(self, line):
        if line.find(";") == -1:
            return self.__isEntireLineComment(line)
        else:
            return line.split(";")[0] + ";"

    # remove what we think is a comment, and check if this entire line comment
    def __isEntireLineComment(self, line):
        fieldChunks = line.split("//")
        return fieldChunks[0].strip()

    def tokenize(self, data):
        # tokenizing line by line
        for line in data:
            sline = line.strip() # make striped line
            # remove what we think is a comment, and check if this entire line comment
            # Note: we still need comments for fields, it is out field description
            if self.__isEntireLineComment(sline):
                if sline.find(pf_required) != -1 or \
                   sline.find(pf_optional) != -1 or \
                   sline.find(pf_repeated) != -1:
                    logging.debug(sline)
                    token = self.createFieldToken(sline)
                    self.__tokens.append(token)
                elif sline.find(pd_package) != -1:
                    logging.debug(sline)
                    token = self.createPackageToken(sline)
                    self.__tokens.append(token)
                elif sline.find(pd_message) != -1:
                    logging.debug(sline)
                    token = self.__createMessageToken(sline)
                    self.__tokens.append(token)
                elif sline.find(pd_end) != -1:
                    logging.debug(sline)
                    token = self.__createEndToken(sline)
                    self.__tokens.append(token)

        return self

