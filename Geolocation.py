1import pygeoip
import jarray
import inspect
import os
from java.lang import Class
from java.lang import System
from java.sql  import DriverManager, SQLException
from java.util.logging import Level
from java.io import File
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.datamodel import ContentUtils
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager



# Factory that defines the name and details of the module and allows Autopsy
# to create instances of the modules that will do the analysis.
class GeoIPlocationFinderIngestModuleFactory(IngestModuleFactoryAdapter):

    moduleName = "GeoIPlocationFinder"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "Finds Skype Data"

    def getModuleVersionNumber(self):
        return "1.0"

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return GeoIPlocationFinderIngestModule()


# Data Source-level ingest module.  One gets created per data source.
class GeoIPlocationFinderIngestModule(DataSourceIngestModule):

    _logger = Logger.getLogger(GeoIPlocationFinderIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self):
        self.context = None

    # Where any setup and configuration is done
    # 'context' is an instance of org.sleuthkit.autopsy.ingest.IngestJobContext.
    # See: http://sleuthkit.org/autopsy/docs/api-docs/3.1/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_ingest_job_context.html
    def startUp(self, context):
        self.context = context

    # Where the analysis is done.
    # The 'dataSource' object being passed in is of type org.sleuthkit.datamodel.Content.
    # See: http://www.sleuthkit.org/sleuthkit/docs/jni-docs/4.3/interfaceorg_1_1sleuthkit_1_1datamodel_1_1_content.html
    # 'progressBar' is of type org.sleuthkit.autopsy.ingest.DataSourceIngestModuleProgress
    # See: http://sleuthkit.org/autopsy/docs/api-docs/3.1/classorg_1_1sleuthkit_1_1autopsy_1_1ingest_1_1_data_source_ingest_module_progress.html
    def process(self, dataSource, progressBar):

        # Find autopsy.db file for a particular case 
        # Add Case folder as data source
        
    
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        files = fileManager.findFiles(dataSource, "%utopsy.db")
        # we don't know how much work there is yet

        progressBar.switchToIndeterminate()

        # This will work in 4.0.1 and beyond
        # Use blackboard class to index blackboard artifacts for keyword search
        # blackboard = Case.getCurrentCase().getServices().getBlackboard()

        numFiles = len(files)
        progressBar.switchToDeterminate(numFiles)
        fileCount = 0;
        for file in files:

            # Check if the user pressed cancel while we were busy
            if self.context.isJobCancelled():
                return IngestModule.ProcessResult.OK

            self.log(Level.INFO, "Processing file: " + file.getName())
            fileCount += 1

        # instantiate a GeoIP class with the location of our uncompressed database 'GeoliteCity.dat'.
        # "CHANGE THE FOLLOWING PATH ACCORDING TO YOUR SYSTEM" #### 
        gi = pygeoip.GeoIP(r'C:\Users\Toshiba\AppData\Roaming\autopsy\python_modules\geolocation\GeoLiteCity.dat')
        
		
		
        #gi = pygeoip.GeoIP(os.getcwd()+'\\'+str('GeoLiteCity.dat'))
        

        # Define function 'Info' to get the resultant directory 
        def Info(tgt):
            rec = gi.record_by_addr(tgt)
            return rec 
        
        

        # Save the DB locally in the temp folder. use file id as name to reduce collisions
        lclDbPath = os.path.join(Case.getCurrentCase().getTempDirectory(), str(file.getId()) + ".db")
        ContentUtils.writeToFile(file, File(lclDbPath))
                        
            # Open the DB using JDBC
        try: 
            Class.forName("org.sqlite.JDBC").newInstance()
            dbConn = DriverManager.getConnection("jdbc:sqlite:%s"  % lclDbPath)
        except SQLException as e:
            self.log(Level.INFO, "Could not open database file (not SQLite) " + file.getName() + " (" + e.getMessage() + ")")
            return IngestModule.ProcessResult.OK

        # Query the 'blackboard_attributes' table in the database and get IP Address column. 
        try:
            stmt = dbConn.createStatement()
            resultSet = stmt.executeQuery("SELECT value_text FROM blackboard_attributes WHERE attribute_type_id = '10';")
            
        except SQLException as e:
            self.log(Level.INFO, "Error querying database for table (" + e.getMessage() + ")")
            return IngestModule.ProcessResult.OK
        

        # Create / open  'GeoIPResult.txt' that will contain the entire inforamtion 
        # regarding a particular IP address  
        outPath = os.path.join(Case.getCurrentCase().getCaseDirectory(), "ModuleOutput","GeoIPResult.txt")
        outFile = open(outPath,'w') 
        # Cycle through each IP address in Ip address column. 
        while resultSet.next():
            try: 
                 
                IP_ADD = resultSet.getString("value_text")

                try:
                    INFO = Info(IP_ADD)
                    latitude = INFO.get('latitude')
                    longitude = INFO.get('longitude')
                        
                    outFile.write(IP_ADD+'  ---------->>  '+str(INFO)+'\n')
                    
                except:
                    outFile.write("Not valid ipaddress"+'\n')
                    

            except SQLException as e:
                self.log(Level.INFO, "Error getting values from table (" + e.getMessage() + ")") 
        

        # Make an artifact on the blackboard,TSK_GPS_TRACKPOINT and give it attributes longitude and latitude.

            art = file.newArtifact(BlackboardArtifact.ARTIFACT_TYPE.TSK_GPS_TRACKPOINT)
            art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_GEO_LONGITUDE .getTypeID(), 
                    GeoIPlocationFinderIngestModuleFactory.moduleName, longitude))
            art.addAttribute(BlackboardAttribute(BlackboardAttribute.ATTRIBUTE_TYPE.TSK_GEO_LATITUDE .getTypeID(), 
                    GeoIPlocationFinderIngestModuleFactory.moduleName, latitude))  
 
   
        # Close .txt file and Db connection 
        outFile.close()            
        stmt.close()
        dbConn.close()
        os.remove(lclDbPath)

            

        return IngestModule.ProcessResult.OK
 
            
           

