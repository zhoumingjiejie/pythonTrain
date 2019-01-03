import json
import urllib2
import urllib
import pandas as pd

class ENCODEQT:
    """This class contains all functions to access the ENCODE TF Significance Tool's JSON-based API."""
    #: private variable that holds the element type as a string.
    _elementType = "genes"
    #: private variable that holds the organism type as a string.
    _organism = "human"
    #: private variable that holds the feature type as a string.
    _featureType = "TSS"
    #: private variable that holds the upstream pad as (-1 * floor(pad_in_bp / 500)).
    _upstream = -1
    #: private variable that holds the downstream pad as (floor(pad_in_bp / 500)).
    _downstream = 1
    #: private variable that holds the symbol type as a string.
    _symbolType = "symbol"
    #: private array that holds one or more arrays of gene or transcript IDs.
    _symbolList = [[]]
    #: private array that holds the names to associate with each list in _symbolList. The number of array elements must match the number of subarrays in _symbolList. Setting this variable is optional for single-list cases (the name "List1" will be used as a default).
    _listNames = []
    #: private array that holds one or more cell line codes to be analyzed. For cases where all cell line data should be pooled, set the array to have a single element "all".
    _cellLines = ["all"]
    #: private array that holds the names of all genes/transcripts to use as a background set. The set of all genes/transcripts in the DB will be used if this array is empty.
    _backgroundList = []
    #: private variable that holds the POST data sent to the server as a JSON-formatted string. Used for troubleshooting.
    _priorQuery = {}
    #: private variable that specifies the type of query using the API.
    _queryType = ''
    
    #: private variable that holds the current URL for the ENCODE TF Significance Tool's API. Used to POST and retrieve data.
    _url = 'http://encodeqt.simple-encode.org/encodeqtAPI.php'
    
    def __init__(self):
        """This function is called upon object instantiation with default parameters including an empty _symbolList variable."""
        self._elementType = "genes"
        self._organism = "human"
        self._featureType = "TSS"
        self._upstream = -1
        self._downstream = 1
        self._symbolType = "symbol"
        self._symbolList = [[]]
        self._listNames = []
        self._cellLines = ["all"]
        self._backgroundList = []
        self._priorQuery = {}
        self._queryType = ''
    
    def getPriorQuery(self):
        """This function returns the most recent data POSTed to the API as a JSON-formatted string. Only queries of type "TFSig" are stored.

        :returns: string -- a JSON-formatted string containing the data POSTed to the API for the most recent "TFsig" query.

        """
        return self._priorQuery
    def setPriorQuery(self,query):
        """This function stores the data to be POSTed to the API as a JSON-formatted string. Only queries of type "TFSig" are stored.

        :param query: A JSON-formatted string that was POSTed to the server for the most recent "TFsig" query.
        :type query: str
        
        """
        self._priorQuery = query
    
    def getElementType(self):
        """This function returns the current value of _elementType.
        
        :returns: str -- the element type to be used for the current query.
        
        """
        return self._elementType
    def setElementType(self,elementType):
        """This function sets the value of _elementType.
        
        :param elementType: the element type to use for the next query ("genes", "transcripts", "pseudogenes", or "pseudotranscripts").
        :type elementType: str
        
        """
        elementType = elementType.lower()
        if elementType != "genes" and elementType != "transcripts" and elementType != "pseudogenes" and elementType != "pseudotranscripts":
            print "Error: argument must be one of the following values: genes, transcripts, pseudogenes, pseudotranscripts. Existing value kept."
            return;
        if elementType == "pseudogenes":
            elementType = "pgenes"
        elif elementType == "pseudotranscripts":
            elementType = "ptranscripts"
        self._elementType = elementType
    
    def getOrganism(self):
        """This function returns the current value of _organism.
        
        :returns: str -- the organism type to be used for the current query.
        
        """
        return self._organism
    def setOrganism(self,organism):
        """This function sets the value of _organism.
        
        :param organism: the organism to query ("human" or "mouse").
        :type organism: str
        
        """
        organism = organism.lower()
        if organism != "human" and organism != "mouse":
            print "Error: argument must be one of the following values: human, mouse. Existing value kept."
            return;
        self._organism = organism

    def getFeatureType(self):
        """This function returns the current value of _featureType.
        
        :returns: str -- the feature type to be used for the current query.
        
        """
        return self._featureType
    def setFeatureType(self,featureType):
        """This function sets the value of _featureType.
        
        :param featureType: The feature type for the query ("TSS", "TTS", or "Genic").
        :type featureType: str
        
        """
        featureType = featureType.lower()
        if featureType != "tss" and featureType != "tts" and featureType != "genic":
            print "Error: argument must be one of the following values: TSS, TTS, Genic. Existing value kept."
            return;
        if featureType == "tss" or featureType == "tts":
           featureType = featureType.upper()
        self._featureType = featureType
    
    def getUpstream(self):
        """This function returns the current value of _upstream, the upstream pad, in basepairs. All values will be divisible by 500.
        
        :returns: int -- the size of the upstream pad in basepairs (the number will be negative, indicating upstream).
        
        """
        return self._upstream * -500
    def setUpstream(self,upstream):
        """This function sets the value of _upstream, the upstream pad. Input should be provided in number of basepairs. Input will be automatically converted to the integer format expected by the API.
        
        :param upstream: The value of the upstream analysis window pad in basepairs. Will be rounded up to nearest multiple of 500 and must be less than 5000.
        :type upstream: int

        """
        if not isinstance( upstream, ( int, long ) ) or upstream > 5000 or upstream < 500:
            print "Error: argument must be a digit between 500 and 5000. Exisiting value kept."
            return;
        if upstream % 500 != 0:
            print "Upstream pad provided is not a multiple of 500.  Using next highest multiple."
        self._upstream = (upstream / 500) * -1
    
    def getDownstream(self):
        """This function returns the current value of _downstream, the downstream pad, in basepairs. All values will be divisible by 500.
    
        :returns: int -- the size of the upstream pad in basepairs (the number will be negative, indicating upstream).
    
        """
        return self._downstream * 500
    def setDownstream(self,downstream):
        """This function sets the value of _downstream, the downstream pad. Input should be provided in number of basepairs. Input will be automatically converted to the integer format expected by the API.

        :param downstream: The value of the downstream analysis window pad in basepairs. Will be rounded up to nearest multiple of 500 and must be less than 5000.
        :type downstream: int

        """
        if not isinstance( downstream, ( int, long ) ) or downstream > 5000 or downstream < 500:
            print "Error: argument must be a digit between 500 and 5000. Exisiting value kept."
            return;
        if downstream % 500 != 0:
            print "Downstream pad provided is not a multiple of 500.  Using next highest multiple."
        self._downstream = downstream / 500
    
    def getSymbolType(self):
        """This function returns the current value of _symbolType.

        :returns: str -- the symbol type to be used for the current query
    
        """
        return self._symbolType
    def setSymbolType(self,symbolType):
        """This function sets the value of _symbolType.
        
        :param symbolType: The symbol type to use for the current query ("symbol", "ensembl", "entrez", or "havana").
        :type symbolType: str
        
        """
        symbolType = symbolType.lower()
        if symbolType != "symbol" and symbolType != "ensembl" and symbolType != "entrez" and symbolType != "havana":
            print "Error: argument must be one of the following values: symbol, ensembl, entrez, havana. Existing value kept."
            return;
        self._symbolType = symbolType

    def getSymbolList(self):
        """This function returns the current value of _symbolList as an array of arrays.
        
        :returns: str[][] -- an array of arrays containing each foreground list of genes/transcripts to be used in the current query."
        
        """
        return self._symbolList
    def setSymbolList(self,symbolList):
        """This function sets the value of _symbolList and expects an array of arrays as input.
        
        :param symbolList: An array of arrays containing lists of genes/transcripts to use as the foreground in the current query.
        :type symbolList: str[][]
        
        """
        if not type(symbolList) is list:
            print "Argument must be a list of lists. Existing value kept."
            return
        else:
            for i in symbolList:
                if not type(i) is list:
                    print "Argument must be a list of lists. Existing value kept."
                    return
        self._symbolList = symbolList

    def getListNames(self):
        """This function returns the current value of _listNames as an array.
        
        :returns: str[] -- an array of labels for each gene/transcript list to be used in the current query.
        
        """
        return self._listNames
    def setListNames(self,listNames):
        """This function sets the value of _listNames given an array of strings as input.
        
        :param listNames: An array of labels to use for each gene/transcript list in the current query. To use the default labels, pass an empty array.
        :type listNames: str[]

        """
        if not type(listNames) is list:
            print "Argument must be a list. Existing value kept."
            return
        self._listNames = listNames

    def getCellLines(self):
        """This function returns the current value of _cellLines.
        
        :returns: str[] -- An array of strings containing the cell type labels to use for the current query. For queries pooled across all cell lines, a single-element array containing "all" is used.
        
        """
        return self._cellLines
    def setCellLines(self,cellLines):
        """This function sets the value of _cellLines given an array of strings (cell line IDs) as input.
        
        :param cellLines: An array of strings containing the cell type labels to use for the current query. For queries pooled across all cell lines, a single-element array containing "all" should be used.
        :type cellLines: str[]

        """
        if not type(cellLines) is list:
            print "Argument must be a list. Existing value kept."
            return
        self._cellLines = cellLines

    def getBackgroundList(self):
        """This function returns the value of _backgroundList as an array.
        
        :returns: str[] -- an array containing the symbols to use for the background data set. An empty array indicates that the background data will be comprised of all symbols in the database.
        
        """
        return self._backgroundList
    def setBackgroundList(self,backgroundList):
        """This function sets the value of _backgroundList given an array of strings as input.
        
        :param backgroundList: an array containing the symbols to use for the background data set. To use the set of all symbols in our database, pass an empty array.
        :type backgroundList: str[]
        
        """
        if not type(backgroundList) is list:
            print "Argument must be a list. Existing value kept."
            return
        self._backgroundList = backgroundList        
    
    def validateOrganism(self):
        """This function validates that _organism is set to a valid value (currently "human" or "mouse"). It is called in the other functions when needed.
        
        :returns: int -- the return code (1 if invalid, 0 if valid)
        
        """
        if self.getOrganism() not in ['human','mouse']:
            print "Error: Invalid organism provided."
            return(1)
        else:
            return(0)

    def validateQuery(self):
        """This function validates that all variables required for query type "TFsig" are set to valid values before POSTing the data to the API. This function is called in the other functions when needed.
        
        :returns: int -- the return code (1 if invalid, 0 if valid)
        
        """
        if self.validateOrganism() == 1:
            return(1)
        if self.getElementType() not in ['genes','transcripts','pgenes','ptranscripts']:
            print "Error: Invalid element type provided."
            return(1)
        if self.getFeatureType() not in ['TSS','TTS','genic']:
            print "Error: Invalid feature type provided."
            return(1)
        if self.getOrganism() == 'human':
            if self.getSymbolType() not in ['symbol','ensembl','entrez','havana']:
                print "Error: Invalid symbol type provided."
                return(1)
            elif self.getElementType() not in ['genes','transcripts','pgenes','ptranscripts']:
                print "Error: Invalid element type provided."
                return(1)
        elif self.getOrganism() == 'mouse':
            if self.getSymbolType() in ['havana']:
                print "Error: Invalid symbol type provided. HAVANA IDs not supported for mouse."
                return(1)
            if self.getSymbolType() not in ['symbol','ensembl','entrez']:
                print "Error: Invalid symbol type provided."
                return(1)
            if self.getElementType() not in ['genes','transcripts']:
                print "Error: Only element types \"genes\" and \"transcripts\" are supported for mouse."
                return(1)
        if self.getElementType() in ['transcripts','ptranscripts'] and self.getSymbolType() == 'entrez':
                print "Error: Entrez is an invalid symbol type for transcripts and ptranscripts."
                return(1)
        if self.getCellLines():
           for i in range(0,len(self._cellLines)):
                if self._cellLines[i] == 'all':
                    next
                else:
                    formattedCellLine = self._cellLines[i][0].upper() + self._cellLines[i][1:].lower()
                    self._cellLines[i] = formattedCellLine
        if not self.getSymbolList()[0]:
            print "Must enter at least one list of gene or transcript IDs."
            return(1)
        else:
            if(self.getOrganism() == 'human'):
                for i in range(0,len(self._symbolList)):
                    for j in range(0,len(self._symbolList[i])):
                        if not isinstance( self._symbolList[i][j], ( int, long ) ):
                            self._symbolList[i][j] = self._symbolList[i][j].upper()
                        if self.getElementType() == "genes" or self.getElementType() == "pgenes":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENSG') or self._symbolList[i][j].startswith('OTTHUMG') or self._symbolList[i][j].isdigit()):
                                print "Gene symbols cannot be integers or start with either \"ENSG\" or \"OTTHUMG\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENSG'):
                                print "Ensembl gene IDs must start with \"ENSG\""
                                return(1)
                            elif self.getSymbolType() == 'havana' and not self._symbolList[i][j].startswith('OTTHUMG'):
                                print "HAVANA gene IDs must start with \"OTTHUMG\""
                                return(1)
                            elif self.getSymbolType() == 'entrez' and not isinstance(self._symbolList[i][j],(int, long)):
                                print "Entrez IDs must be integers"
                                return(1)
                        elif self.getElementType() == "transcripts" or self.getElementType() == "ptranscripts":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENST') or self._symbolList[i][j].startswith('OTTHUMT') or self._symbolList[i][j].isdigit()):
                                print "Transcript symbols cannot be integers or start with either \"ENST\" or \"OTTHUMT\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENST'):
                                print "Ensembl transcript IDs must start with \"ENST\""
                                return(1)
                            elif self.getSymbolType() == 'havana' and not self._symbolList[i][j].startswith('OTTHUMT'):
                                print "HAVANA transcript IDs must start with \"OTTHUMT\""
                                return(1)
            if(self.getOrganism() == 'mouse'):
                for i in range(0,len(self._symbolList)):
                    for j in range(0,len(self._symbolList[i])):
                        if not isinstance( self._symbolList[i][j], ( int, long ) ):
                            self._symbolList[i][j] = self._symbolList[i][j].upper()
                        if self.getElementType() == "genes":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENSMUSG') or self._symbolList[i][j].isdigit()):
                                print "Gene symbols cannot be integers or start with \"ENSMUSG\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENSMUSG'):
                                print "Ensembl gene IDs must start with \"ENSMUSG\""
                                return(1)
                            elif self.getSymbolType() == 'entrez' and not isinstance(self._symbolList[i][j],(int, long)):
                                print "Entrez IDs must be integers"
                                return(1)
                        elif self.getElementType() == "transcripts":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENSMUST') or self._symbolList[i][j].isdigit()):
                                print "Transcript symbols cannot be integers or start with \"ENSMUST\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENSMUST'):
                                print "Ensembl transcript IDs must start with \"ENSMUST\""
                                return(1)
        if self.getBackgroundList():
            if self.getOrganism() == 'human':
                for i in range(0,len(self._backgroundList)):
                    if not isinstance( self._backgroundList[i], ( int, long ) ):
                        self._backgroundList[i] = self._backgroundList[i].upper()
                    if self.getElementType() == "genes" or self.getElementType() == "pgenes":
                        if self.getSymbolType() == 'symbol' and (isinstance(self._backgroundList[i],(int, long)) or self._backgroundList[i].startswith('ENSG') or self._backgroundList[i].startswith('OTTHUMG') or self._backgroundList[i].isdigit()):
                            print "Gene symbols cannot be integers or start with either \"ENSG\" or \"OTTHUMG\""
                            return(1)
                        elif self.getSymbolType() == 'ensembl' and not self._backgroundList[i].startswith('ENSG'):
                            print "Ensembl gene IDs must start with \"ENSG\""
                            return(1)
                        elif self.getSymbolType() == 'havana' and not self._backgroundList[i].startswith('OTTHUMG'):
                            print "HAVANA gene IDs must start with \"OTTHUMG\""
                            return(1)
                        elif self.getSymbolType() == 'entrez' and not isinstance(self._backgroundList[i],(int, long)):
                            print "Entrez IDs must be integers"
                            return(1)
                    elif self.getElementType() == "transcripts" or self.getElementType() == "ptranscripts":
                        if self.getSymbolType() == 'symbol' and (isinstance(self._backgroundList[i],(int, long)) or self._backgroundList[i].startswith('ENST') or self._backgroundList[i].startswith('OTTHUMT') or self._backgroundList[i].isdigit()):
                            print "Transcript symbols cannot be integers or start with either \"ENST\" or \"OTTHUMT\""
                            return(1)
                        elif self.getSymbolType() == 'ensembl' and not self._backgroundList[i].startswith('ENST'):
                            print "Ensembl transcript IDs must start with \"ENST\""
                            return(1)
                        elif self.getSymbolType() == 'havana' and not self._backgroundList[i].startswith('OTTHUMT'):
                            print "HAVANA transcript IDs must start with \"OTTHUMT\""
                            return(1)
                        elif self.getSymbolType() == 'entrez' and not isinstance(_backgroundList[i],(int, long)):
                            print "Entrez IDs must be integers"
                            return(1)
            elif self.getOrganism() == 'mouse':
                for i in range(0,len(self._backgroundList)):
                    if not isinstance( self._backgroundList[i], ( int, long ) ):
                        self._backgroundList[i] = self._backgroundList[i].upper()
                    if self.getElementType() == "genes":
                        if self.getSymbolType() == 'symbol' and (isinstance(self._backgroundList[i],(int, long)) or self._backgroundList[i].startswith('ENSMUSG') or self._backgroundList[i].isdigit()):
                            print "Gene symbols cannot be integers or start with \"ENSMUSG\""
                            return(1)
                        elif self.getSymbolType() == 'ensembl' and not self._backgroundList[i].startswith('ENSMUSG'):
                            print "Ensembl gene IDs must start with \"ENSMUSG\""
                            return(1)
                        elif self.getSymbolType() == 'entrez' and not isinstance(self._backgroundList[i],(int, long)):
                            print "Entrez IDs must be integers"
                            return(1)
                    elif self.getElementType() == "transcripts":
                        if self.getSymbolType() == 'symbol' and (isinstance(self._backgroundList[i],(int, long)) or self._backgroundList[i].startswith('ENSMUST') or self._backgroundList[i].isdigit()):
                            print "Transcript symbols cannot be integers or start with \"ENSMUST\""
                            return(1)
                        elif self.getSymbolType() == 'ensembl' and not self._backgroundList[i].startswith('ENSMUST'):
                            print "Ensembl transcript IDs must start with \"ENSMUST\""
                            return(1)
        if self.getListNames():
            if len(self.getListNames()) != len(self.getSymbolList()):
                print "If list names are provided, the number of list names must match the number of symbol lists."
                return(1)
        if self.getFeatureType() == "genic":
            if abs(self.getUpstream()) != self.getDownstream():
                print "Warning: For genic analysis, values for upstream and downstream must have the same absolute value. Using the upstream pad..."
                self.setDownstream(self.getUpstream() * -1)
        if self.getUpstream() > 5000 or self.getUpstream() < 500:
            print "Invalid upstream pad value."
            return(1)
        if self.getDownstream() < 500 or self.getDownstream() > 5000:
            print "Invalid downstream pad value."
            return(1)
        return(0)
    
    def validateCheckGeneInDBQuery(self):
        """This function validates that all variables necessary for query type "geneCheck" are set to valid values before POSTing the data to the API. This function is called in the other functions when needed.
        
        :returns: int -- the return code (1 if invalid, 0 if valid)
        
        """
        if self.validateOrganism() == 1:
            return(1)
        if self.getElementType() not in ['genes','transcripts','pgenes','ptranscripts']:
            print "Error: Invalid element type provided."
            return(1)
        if self.getOrganism() == 'human':
            if self.getSymbolType() not in ['symbol','ensembl','entrez','havana']:
                print "Error: Invalid symbol type provided."
                return(1)
            elif self.getElementType() not in ['genes','transcripts','pgenes','ptranscripts']:
                print "Error: Invalid element type provided."
                return(1)
        elif self.getOrganism() == 'mouse':
            if self.getSymbolType() in ['havana']:
                print "Error: Invalid symbol type provided. HAVANA IDs not supported for mouse."
                return(1)
            if self.getSymbolType() not in ['symbol','ensembl','entrez']:
                print "Error: Invalid symbol type provided."
                return(1)
            if self.getElementType() not in ['genes','transcripts']:
                print "Error: Only element types \"genes\" and \"transcripts\" are supported for mouse."
                return(1)
        if self.getElementType() in ['transcripts','ptranscripts'] and self.getSymbolType() == 'entrez':
                print "Error: Entrez is an invalid symbol type for transcripts and ptranscripts."
                return(1)
        if not self.getSymbolList()[0]:
            print "Must enter at least one list of gene or transcript IDs."
            return(1)
        else:
            if(self.getOrganism() == 'human'):
                for i in range(0,len(self._symbolList)):
                    for j in range(0,len(self._symbolList[i])):
                        if not isinstance( self._symbolList[i][j], ( int, long ) ):
                            self._symbolList[i][j] = self._symbolList[i][j].upper()
                        if self.getElementType() == "genes" or self.getElementType() == "pgenes":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENSG') or self._symbolList[i][j].startswith('OTTHUMG') or self._symbolList[i][j].isdigit()):
                                print "Gene symbols cannot be integers or start with either \"ENSG\" or \"OTTHUMG\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENSG'):
                                print "Ensembl gene IDs must start with \"ENSG\""
                                return(1)
                            elif self.getSymbolType() == 'havana' and not self._symbolList[i][j].startswith('OTTHUMG'):
                                print "HAVANA gene IDs must start with \"OTTHUMG\""
                                return(1)
                            elif self.getSymbolType() == 'entrez' and not isinstance(self._symbolList[i][j],(int, long)):
                                print "Entrez IDs must be integers"
                                return(1)
                        elif self.getElementType() == "transcripts" or self.getElementType() == "ptranscripts":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENST') or self._symbolList[i][j].startswith('OTTHUMT') or self._symbolList[i][j].isdigit()):
                                print "Transcript symbols cannot be integers or start with either \"ENST\" or \"OTTHUMT\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENST'):
                                print "Ensembl transcript IDs must start with \"ENST\""
                                return(1)
                            elif self.getSymbolType() == 'havana' and not self._symbolList[i][j].startswith('OTTHUMT'):
                                print "HAVANA transcript IDs must start with \"OTTHUMT\""
                                return(1)
            elif(self.getOrganism() == 'mouse'):
                for i in range(0,len(self._symbolList)):
                    for j in range(0,len(self._symbolList[i])):
                        if not isinstance( self._symbolList[i][j], ( int, long ) ):
                            self._symbolList[i][j] = self._symbolList[i][j].upper()
                        if self.getElementType() == "genes":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENSMUSG') or self._symbolList[i][j].isdigit()):
                                print "Gene symbols cannot be integers or start with \"ENSMUSG\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENSMUSG'):
                                print "Ensembl gene IDs must start with \"ENSMUSG\""
                                return(1)
                            elif self.getSymbolType() == 'entrez' and not isinstance(self._symbolList[i][j],(int, long)):
                                print "Entrez IDs must be integers"
                                return(1)
                        elif self.getElementType() == "transcripts":
                            if self.getSymbolType() == 'symbol' and (isinstance(self._symbolList[i][j],(int, long)) or self._symbolList[i][j].startswith('ENSMUST') or self._symbolList[i][j].isdigit()):
                                print "Transcript symbols cannot be integers or start with \"ENSMUST\""
                                return(1)
                            elif self.getSymbolType() == 'ensembl' and not self._symbolList[i][j].startswith('ENSMUST'):
                                print "Ensembl transcript IDs must start with \"ENSMUST\""
                                return(1)
        return(0)
    
    def validateAllGenesQuery(self):
        """This function validates that all variables necessary for query type "allGenes" are set to valid values before POSTing the data to the API. This function is called in the other functions when needed.
        
        :returns: int -- the return code (1 if invalid, 0 if valid)
        
        """
        if self.validateOrganism() == 1:
            return(1)
        if self.getElementType() not in ['genes','transcripts','pgenes','ptranscripts']:
            print "Error: Invalid element type provided."
            return(1)
        if self.getFeatureType() not in ['TSS','TTS','genic']:
            print "Error: Invalid feature type provided."
            return(1)
        if self.getOrganism() == 'human':
            if self.getSymbolType() not in ['symbol','ensembl','entrez','havana']:
                print "Error: Invalid symbol type provided."
                return(1)
            elif self.getElementType() not in ['genes','transcripts','pgenes','ptranscripts']:
                print "Error: Invalid element type provided."
                return(1)
        elif self.getOrganism() == 'mouse':
            if self.getSymbolType() in ['havana']:
                print "Error: Invalid symbol type provided. HAVANA IDs not supported for mouse."
                return(1)
            if self.getSymbolType() not in ['symbol','ensembl','entrez']:
                print "Error: Invalid symbol type provided."
                return(1)
            if self.getElementType() not in ['genes','transcripts']:
                print "Error: Only element types \"genes\" and \"transcripts\" are supported for mouse."
                return(1)
        if self.getElementType() in ['transcripts','ptranscripts'] and self.getSymbolType() == 'entrez':
            print "Error: Entrez is an invalid symbol type for transcripts and ptranscripts."
            return(1)
        if self.getCellLines():
           for i in range(0,len(self._cellLines)):
                if self._cellLines[i] == 'all':
                    next
                else:
                    formattedCellLine = self._cellLines[i][0].upper() + self._cellLines[i][1:].lower()
                    self._cellLines[i] = formattedCellLine        
        if self.getFeatureType() == "genic":
            if abs(self.getUpstream()) != self.getDownstream():
                print "Warning: For genic analysis, values for upstream and downstream must have the same absolute value. Using the upstream pad..."
                self.setDownstream(self.getUpstream() * -1)
        if self.getUpstream() > 5000 or self.getUpstream() < 500:
            print "Invalid upstream pad value."
            return(1)
        if self.getDownstream() < 500 or self.getDownstream() > 5000:
            print "Invalid downstream pad value."
            return(1)
        return(0)

    def useSampleQuery(self):
        """Sets al values equivalent to those needed to run Demo #1 on the encodeqt.stanford.edu website.  Used for testing purposes."""
        self.setElementType("genes")
        self.setOrganism("human")
        self.setFeatureType("TSS")
        self.setUpstream(2000)
        self.setDownstream(2000)
        self.setSymbolType("symbol")
        self.setListNames(["AAYRNCTG_Motifs"])
        self.setCellLines(["all"])
        self.setSymbolList([["ABT1","ACVR1","ADAM12","ADD3","AGGF1","ANKRD12","ANKRD28","AP4S1","APBB2","APOBR","AQP2","ARHGAP44","ARID1A","ARID4A","ARPC2","ARSG","ARX","ASB4","ASPH","ATOH8","ATP1A2","ATP5L","ATPIF1","AXDND1","B4GALT6","BAI3","BAMBI","BCL2L1","BCL9","BMPR1B","BMX","BRSK2","BTBD3","BUB3","C11ORF84","C11ORF92","C12ORF65","C13ORF30","C14ORF1","C15ORF26","C17ORF28","C20ORF197","C3ORF19","C6ORF138","CA3","CACNA2D3","CACNB2","CAPN1","CAPZA1","CASQ2","CBX2","CCNJ","CCNY","CDC23","CDH2","CER1","CHRM1","CITED2","CLDN5","CLTC","CMKLR1","CNTLN","CNTN1","COCH","COL12A1","COL1A2","COL4A5","COL4A6","COLEC10","CRAT","CRH","CRKL","CRYGD","CRYGS","CSNK1A1","CSRNP3","CSTF3","CYBRD1","DAAM1","DBNDD2","DCAKD","DDAH2","DDX4","DEF6","DENND4A","DGKB","DHH","DHRS4","DHRS4L2","DIDO1","DMD","DMRT1","DNAJA2","DNAJB3","DNAJB4","DSCAML1","DUSP4","DYNC1I1","DYRK1A","EDA","EFNA1","EGFLAM","EIF5","EMX2","EPC1","EPHA7","ERBB4","ERRFI1","ESRP2","ESRRB","ESRRG","EYA1","FAM49A","FAM83F","FCER1A","FGD4","FGF10","FGF12","FGFR1","FGFR1OP2","FIZ1","FKRP","FMNL3","FNDC9","FOXA1","FOXG1","FOXO4","FOXP2","FSIP2","FST","GABRA3","GDNF","GFI1","GGNBP2","GJB4","GLDN","GNAQ","GPR85","GPRC5D","GRIN2B","H3F3A","HDAC8","HESX1","HEXIM2","HGF","HIC2","HIP1R","HN1","HOXA10","HOXA5","HOXB8","HPSE2","HSD3B7","ICAM4","ID1","IGF1","IL1RAPL1","INHBC","IP6K2","ITGA10","ITGA8","JPH1","KANK2","KCNIP2","KCNK5","KCNN3","KCNQ1DN","KIAA0182","KITLG","KLF5","KLHDC10","KLHL20","KLHL3","LARS2","LENG9","LHFP","LHX9","LMO7","LOC151534","LRP5","LRRC4","LRRN4CL","LTBP1","MAML1","MANF","MAP2","MAP3K5","MAP6","MEIS1","MGAT1","MGAT4A","MID1","MLL","MOAP1","MPP6","MPPED2","MRPL13","MTA2","MTBP","MYF6","MYH1","MYH10","MYO18A","NAGLU","NAPB","NAV2","NAV3","NCDN","NDNF","NDST4","NDUFS4","NEK1","NEK2","NFATC4","NFYB","NMI","NMT1","NR2F1","NRG1","NTRK2","NUP54","NXPH4","OMA1","OMG","OR2L13","OTX2","PACRG","PAPD5","PARK2","PART1","PCDH17","PCDH18","PCF11","PCYT1B","PDGFB","PDGFRA","PDLIM2","PDS5B","PDZRN4","PFN2","PHC2","PHEX","PHF1","PHF15","PHF6","PHOX2B","PLAGL2","PLEC","PLEKHM1","PLP2","PMCH","PMCHL1","PODXL2","POFUT1","POU2AF1","POU4F1","PPAP2B","PPP1R9B","PPP2R3A","PPP2R4","PPP2R5E","PPP3CA","PRELP","PRKCG","PRKCQ","PROK2","PTH1R","PXN","R3HDM1","RAB30","RAB5B","RAB5C","RAPGEF4","RBMS3","RGS17","RNF146","ROBO4","ROR1","RPLP0","RTN1","RUFY3","S1PR2","SCN3B","SCN5A","SCN8A","SCOC","SDCBP","SEMA6D","SEPT7","SESN3","SGCD","SH2D6","SHC3","SHCBP1L","SIPA1","SIRPA","SLC26A6","SLC4A1","SLC6A1","SMARCA2","SNX9","SORBS2","SOX12","SOX21","SOX30","SOX5","SPOCK2","SPTLC2","SRGAP2","SRSF8","SSBP2","ST7L","STAC3","STAG1","STAG2","STC2","STRN3","STRN4","TAS1R2","TEF","TFAP4","TFDP2","TM2D3","TMEM182","TMEM27","TMEM69","TMSB4X","TMSB4XP1","TMSL3","TMSL6","TNFAIP8","TNS1","TNXB","TP53INP2","TRDN","TREML1","TRIM28","TRIM68","TRIM8","TRIML1","TRPS1","TSC22D3","TSPAN7","TSPY26P","TSSK3","TTC17","TUSC2","UBE2W","UBXN10","USP1","VDR","VIP","VKORC1L1","VWA5A","WBP1","WNT2B","WT1","WT1-AS","XRCC1","ZADH2","ZBTB11","ZFP91","ZFPM2","ZIC1","ZIC4","ZMAT3","ZNF238","ZNF296","ZNF503","ZNF521","ZNF524","ZNF654","ZNF687","ZNF710"]])
        self.setBackgroundList([])

    def showCurrentState(self):
        """This function prints the current values of all variables required for queries."""
        print "Current object attributes:"
        if self._queryType != '':
            print "Query type is: " + self._queryType
        else:
            print "Query type is: Not Set"
        print "Organism type is: " + self.getOrganism()
        print "Element type is: " + self.getElementType()
        print "Feature type is: " + self.getFeatureType()
        print "Symbol type is: " + self.getSymbolType()
        print "Upstream pad is: " + str(self.getUpstream() * -1)
        print "Downstream pad is: " + str(self.getDownstream())
        print "Cell lines are: " + str(self.getCellLines())
        print "List names are: " + str(self.getListNames())
        print "Symbol lists are: " + str(self.getSymbolList())
        if self.getBackgroundList():
            print "Background list is: " + str(self.getBackgroundList())
        else:
            print "Background list is: Entire database"

    def getSignificanceScores(self,format='pandas'):
        """This function calculates significantly enriched transcription factors in one or more gene lists using current variable values.
        
        :param format: The format to use for the output. 'pandas' will output a Pandas DataFrame object. 'json' will output a JSON-formatted string.
        :type format: str
        
        :returns: pandas.DataFrame if format='pandas' or str in JSON format if format='json'.
        
        """
        self._queryType = 'TFsig'
        if self.validateQuery() != 0:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return
        blah = {'queryType' : self._queryType, 'elementType' : self._elementType, 'organism' : self._organism, 'featureType' : self._featureType, 'symbolType' : self._symbolType, 'symbolList' : self._symbolList, 'cellLines' : self._cellLines, 'upstream' : self._upstream, 'downstream' : self._downstream}
        
        if self._listNames:
            blah['listNames'] = self._listNames
        if self._backgroundList:
            blah['backgroundList'] = self._backgroundList
        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        self.setPriorQuery(json.dumps(blah, sort_keys=True, indent=4, separators=(',', ': ')))

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        
        if format == 'json':
            return json.dumps(resultData, sort_keys=True, indent=4, separators=(',', ': '))
        
        #else return a pandas data frame
        resultDict = self.getStatistics(resultData)

        dataList = []
        columns = ['List','Factor','observed','total','pval','rank']
        listNames = resultDict.keys()
        for listName in listNames:
            factors = resultDict[listName].keys()
            for factor in factors:
                if resultDict[listName][factor]['pval'] == "NA":
                    resultDict[listName][factor]['pval'] = 1
                dataList.append((listName,factor,int(resultDict[listName][factor]['observed']),int(resultDict[listName][factor]['total']),float(resultDict[listName][factor]['pval']),int(resultDict[listName][factor]['rank'])))
        z = pd.DataFrame(dataList,columns=columns)
        sortedFrame = z.sort(['List','rank','pval'],ascending=[1,1,1])
        return sortedFrame

    def getAllFactorGenes(self,factor,format='pandas'):
        """This function returns all genes/transcripts in our database with a transcription factor target window intersection given current variable values.
        
        :param format: The format to use for the output. 'pandas' will output a Pandas DataFrame object. 'json' will output a JSON-formatted string.
        :type format: str
        
        :returns: pandas.DataFrame if format='pandas' or str in JSON format if format='json'.

        """
        self._queryType = 'allGenes'
        if self.validateAllGenesQuery() != 0:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return
        
        factor = factor.upper()[0] + factor.lower()[1:]
        
        blah = {'queryType' : self._queryType, 'elementType' : self._elementType, 'organism' : self._organism, 'featureType' : self._featureType, 'cellLines' : self._cellLines, 'upstream' : self._upstream, 'downstream' : self._downstream, 'factorTarget' : factor, 'symbolType' : self._symbolType}
        
        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        
        if format == 'json':
            return json.dumps(resultData, sort_keys=True, indent=4, separators=(',', ': '))
        
        #else return a pandas data frame
        resultDict = self.getStatistics(resultData)
        a=pd.DataFrame(resultDict)
        a=a.reindex_axis(['factorGenes','symbols','ensembl','entrez','description'],axis=1)
        a=a.rename(columns={'factorGenes' : 'Your_Query','symbols' : 'HGNC_Symbol','ensembl' : 'Ensembl','entrez' : 'Entrez','description' : 'Description'})
        sortedFrame = a.sort(['Your_Query'],ascending=[1,])
        return sortedFrame

    def getSigGenesFromListForFactor(self,factor,format='pandas',listToUse='List1'):
        """This function returns all genes/transcripts in the user-provided gene list with a transcription factor target window intersection given current variable values.
        
        :param format: The format to use for the output. 'pandas' will output a Pandas DataFrame object. 'json' will output a JSON-formatted string.
        :type format: str
        :param listToUse: For queries that use multiple foreground lists, the label corresponding to the list to use for this query. The default value of 'List1' is used for single foreground list queries where the _listNames variable is not set.
        :type listToUse: str
        
        :returns: pandas.DataFrame if format='pandas' or str in JSON format if format='json'.
        
        """
        self._queryType = 'listGenes'
        if self.validateQuery() != 0:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return
        
        factor = factor.upper()[0] + factor.lower()[1:]
        
        blah = {'queryType' : self._queryType, 'targetList' : listToUse, 'elementType' : self._elementType, 'organism' : self._organism, 'featureType' : self._featureType, 'symbolType' : self._symbolType, 'symbolList' : self._symbolList, 'cellLines' : self._cellLines, 'upstream' : self._upstream, 'downstream' : self._downstream, 'factorTarget' : factor}

        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        
        if format == 'json':
            return json.dumps(resultData, sort_keys=True, indent=4, separators=(',', ': '))
        
        #else return a pandas data frame
        resultDict = self.getStatistics(resultData)
        dataList = []
        a=pd.DataFrame(resultDict)
        a=a.reindex_axis(['factorGenes','symbols','ensembl','entrez','description'],axis=1)
        a=a.rename(columns={'factorGenes' : 'Your_Query','symbols' : 'HGNC_Symbol','ensembl' : 'Ensembl','entrez' : 'Entrez','description' : 'Description'})
        sortedFrame = a.sort(['Your_Query'],ascending=[1,])
        return sortedFrame

    def verifyFactorInDB(self,factor):
        """Given a transcription factor label, this function verifies that it is in the database.
        
        :param factor: The label corresponding to the transcription factor label to check in the database.
        :type factor: str
        
        :returns: bool -- whether the label exists in the database.
        
        """
        self._queryType = 'validateTF'
        
        if self.validateOrganism() == 1:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return
        
        factor = factor.upper()[0] + factor.lower()[1:]
        
        if factor == "":
            print "Error: Factor value must be non-blank."
            return
        
        blah = {'queryType' : self._queryType, 'organism' : self._organism,'targetFactor' : factor}

        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        
        resultDict = self.getStatistics(resultData)
        if resultDict['valid'] == 1:
            return True
        else:
            return False

    def verifyCellLineInDB(self,cellLine):
        """Given a cell type label, this function verifies that it is in the database.
        
        :param cellLine: The label corresponding to the cell type label to check in the database.
        :type cellLine: str
        
        :returns: bool -- whether the label exists in the database.

        
        """
        self._queryType = 'validateCellLine'
        
        if self.validateOrganism() == 1:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return

        factor = cellLine.upper()[0] + cellLine.lower()[1:]
        
        if cellLine == "":
            print "Error: Cell line value must be non-blank."
            return
        
        blah = {'queryType' : self._queryType, 'organism' : self._organism,'targetCellLine' : cellLine}

        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())

        resultDict = self.getStatistics(resultData)
        if resultDict['valid'] == 1:
            return True
        else:
            return False
        
    def fuzzyFactorSearch(self,factor,format='pandas'):
        """Given a partial transcription factor label, this function performs a fuzzy search to find potential matching labels in the database.
        
        :param factor: a string to match against transcription factor labels in the database.
        :type factor: str
        :param format: The format to use for the output. 'pandas' will output a Pandas DataFrame object. 'json' will output a JSON-formatted string.
        :type format: str

        
        :returns: pandas.DataFrame if format='pandas' or str in JSON format if format='json'.
        
        """
        self._queryType = 'fuzzyFactorSearch'
        
        if self.validateOrganism() == 1:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return

        factor = factor.upper()[0] + factor.lower()[1:]
        
        if factor == "":
            print "Error: Factor value must be non-blank."
            return
        
        blah = {'queryType' : self._queryType, 'organism' : self._organism,'targetFactor' : factor}

        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        
        if format == 'json':
            return json.dumps(resultData, sort_keys=True, indent=4, separators=(',', ': '))
        
        #else return a pandas data frame
        resultDict = self.getStatistics(resultData)

        a=pd.DataFrame(resultDict)
        a=a.rename(columns={0 : 'Factor'})
        sortedFrame = a.sort(['Factor'],ascending=[1,])
        return sortedFrame

    def fuzzyCellLineSearch(self,cellLine,format='pandas'):
        """Given a partial cell type label, this function performs a fuzzy search to find potential matching labels in the database.
        
        :param cellLine: a string to match against cell type labels in the database.
        :type cellLine: str
        :param format: The format to use for the output. 'pandas' will output a Pandas DataFrame object. 'json' will output a JSON-formatted string.
        :type format: str

        :returns: pandas.DataFrame if format='pandas' or str in JSON format if format='json'.

        
        """
        self._queryType = 'fuzzyCellLineSearch'
        
        if self.validateOrganism() == 1:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return

        cellLine = cellLine.upper()[0] + cellLine.lower()[1:]
        
        if cellLine == "":
            print "Error: Cell line value must be non-blank."
            return
        
        blah = {'queryType' : self._queryType, 'organism' : self._organism,'targetCellLine' : cellLine}

        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        
        if format == 'json':
            return json.dumps(resultData, sort_keys=True, indent=4, separators=(',', ': '))
        
        #else return a pandas data frame
        resultDict = self.getStatistics(resultData)

        a=pd.DataFrame(resultDict)
        a=a.rename(columns={0 : 'Cell_Type'})
        sortedFrame = a.sort(['Cell_Type'],ascending=[1,])
        return sortedFrame

    def getTFsAndCellLines(self,format='pandas'):
        """This function returns all transcription factor/cell type combinations in the database.
        
        :param format: The format to use for the output. 'pandas' will output a Pandas DataFrame object. 'json' will output a JSON-formatted string.
        :type format: str

        :returns: pandas.DataFrame if format='pandas' or str in JSON format if format='json'. For JSON format, two arrays are returned in which the elements correspond (ex: factor #1 and cell type #1, etc).
                                                                                                                                                                         
        """
        self._queryType = 'getTFsAndCellLines'
        
        if self.validateOrganism() == 1:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return

        blah = {'queryType' : self._queryType, 'organism' : self._organism}

        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
                
        if format == 'json':
            return json.dumps(resultData, sort_keys=True, indent=4, separators=(',', ': '))
        
        #else return a pandas data frame
        resultDict = self.getStatistics(resultData)

        a=pd.DataFrame(resultDict)
        a=a.reindex_axis(['factors','cell_lines'],axis=1)
        a=a.rename(columns={'factors' : 'Factor','cell_lines' : 'Cell_Type'})
        sortedFrame = a.sort(['Factor'],ascending=[1,])
        return sortedFrame

    def getTotalGenesAnalyzed(self):
        """For _queryType="TFsig", this function returns the total number of genes comprising the background data set used).
        
        :returns: int -- the total number of genes used for the background data set in the current query.
        
        """
        self._queryType = 'TFsig'
        if self.validateQuery() != 0:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return
        blah = {'queryType' : self._queryType, 'elementType' : self._elementType, 'organism' : self._organism, 'featureType' : self._featureType, 'symbolType' : self._symbolType, 'symbolList' : self._symbolList, 'cellLines' : self._cellLines, 'upstream' : self._upstream, 'downstream' : self._downstream}
        
        if self._listNames:
            blah['listNames'] = self._listNames
        if self._backgroundList:
            blah['backgroundList'] = self._backgroundList
        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        self.setPriorQuery(json.dumps(blah, sort_keys=True, indent=4, separators=(',', ': ')))

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        return int(resultData['totalGenesAnalyzed'])
    
    def getCountsByList(self,results):
        """For _queryType="TFsig", this function returns the number of genes/transcripts with hits in the database for each foreground symbol list.
        
        :returns: int[] -- an array cotaining the number of genes/transcripts with hits in the database for all foreground symbol lists.
        
        """
        self._queryType = 'TFsig'
        if self.validateQuery() != 0:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return
        blah = {'queryType' : self._queryType, 'elementType' : self._elementType, 'organism' : self._organism, 'featureType' : self._featureType, 'symbolType' : self._symbolType, 'symbolList' : self._symbolList, 'cellLines' : self._cellLines, 'upstream' : self._upstream, 'downstream' : self._downstream}
        
        if self._listNames:
            blah['listNames'] = self._listNames
        if self._backgroundList:
            blah['backgroundList'] = self._backgroundList
        #print query
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        self.setPriorQuery(json.dumps(blah, sort_keys=True, indent=4, separators=(',', ': ')))

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        return resultData['countsByList']

    def checkGenesInDB(self,format='pandas'):
        """Given a single gene list, this function will return a JSON-formatted string or a pandas data frame showing which gene/transcript IDs in the list are in the database.
        
        :param format: The format to use for the output. 'pandas' will output a Pandas DataFrame object. 'json' will output a JSON-formatted string.
        :type format: str

        :returns: pandas.DataFrame if format='pandas' or str in JSON format if format='json'.
        """
        self._queryType = 'geneCheck'
        if self.validateCheckGeneInDBQuery() != 0:
            print "ERROR: Query not submitted to server. Please correct errors and resubmit."
            return
        blah = {'queryType' : self._queryType, 'elementType' : self._elementType, 'organism' : self._organism, 'symbolType' : self._symbolType, 'symbolList' : self._symbolList}
        
        bulkData = json.dumps(blah)
        
        postData = urllib.urlencode({'JSONparams':bulkData})

        req = urllib2.Request(self._url,postData)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(req)
        resultData = json.loads(response.read())
        if format == 'json':
            return json.dumps(resultData, sort_keys=True, indent=4, separators=(',', ': '))
        
        #else return a pandas data frame
        resultDict = self.getStatistics(resultData)
        
        dataList = []
        columns = ['ID','In_Database?']
        geneIDs = resultDict.keys()
        for geneID in geneIDs:
            dataList.append((geneID,bool(resultDict[geneID])))
        z = pd.DataFrame(dataList,columns=columns)
        sortedFrame = z.sort(['In_Database?','ID'],ascending=[1,1])
        return sortedFrame

    def getStatistics(self,results):
        """This function extracts the results array returned by all API calls. This array is then used by other functions for furhter processing. Other functions call this function as needed.
        
        :returns: str[] -- The array contained in the results field obtained from the server's response.
        
        """
        return results['results']
        
