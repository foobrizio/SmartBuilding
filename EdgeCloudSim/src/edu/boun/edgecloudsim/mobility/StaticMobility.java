package edu.boun.edgecloudsim.mobility;


import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;
import java.util.Map.Entry;

import org.apache.commons.math3.distribution.ExponentialDistribution;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import edu.boun.edgecloudsim.core.SimSettings;
import edu.boun.edgecloudsim.utils.Location;
import edu.boun.edgecloudsim.utils.SimLogger;
import edu.boun.edgecloudsim.utils.SimUtils;

public class StaticMobility extends MobilityModel {
    private List<TreeMap<Double, Location>> treeMapArray;

    public StaticMobility (int _numberOfMobileDevices, double _simulationTime) {
        super(_numberOfMobileDevices, _simulationTime);
    }


    @Override
    public void initialize() {
        // TODO Auto-generated method stub
        treeMapArray = new ArrayList<TreeMap<Double, Location>>();

        ExponentialDistribution[] expRngList = new ExponentialDistribution[SimSettings.getInstance().getNumOfEdgeDatacenters()];

        Document doc = SimSettings.getInstance().getEdgeDevicesDocument();
        NodeList datacenterList = doc.getElementsByTagName("datacenter");
        for(int i=0; i<datacenterList.getLength(); i++) {
            Node datacenterNode = datacenterList.item(i);
            Element datacenterElement = (Element) datacenterNode;
            Element location = (Element)datacenterElement.getElementsByTagName("location").item(0);
            String attractiveness = location.getElementsByTagName("attractiveness").item(0).getTextContent();
			int placeTypeIndex = Integer.parseInt(attractiveness);
            expRngList[i] = new ExponentialDistribution(SimSettings.getInstance().getMobilityLookUpTable()[placeTypeIndex]);
        }

        for (int i=0; i<numberOfMobileDevices; i++) {
            treeMapArray.add(i, new TreeMap<Double, Location>());
			
			int randDatacenterId = SimUtils.getRandomNumber(0, SimSettings.getInstance().getNumOfEdgeDatacenters()-1);
			Node datacenterNode = datacenterList.item(randDatacenterId);
			Element datacenterElement = (Element) datacenterNode;
			Element location = (Element)datacenterElement.getElementsByTagName("location").item(0);
			String attractiveness = location.getElementsByTagName("attractiveness").item(0).getTextContent();
			int placeTypeIndex = Integer.parseInt(attractiveness);
			int wlan_id = Integer.parseInt(location.getElementsByTagName("wlan_id").item(0).getTextContent());
			int x_pos = Integer.parseInt(location.getElementsByTagName("x_pos").item(0).getTextContent());
			int y_pos = Integer.parseInt(location.getElementsByTagName("y_pos").item(0).getTextContent());

			//start locating user shortly after the simulation started (e.g. 10 seconds)
			treeMapArray.get(i).put(SimSettings.CLIENT_ACTIVITY_START_TIME, new Location(placeTypeIndex, wlan_id, x_pos, y_pos));
        }
        

        
    }

    @Override
    public Location getLocation(int deviceId, double time) {
        // TODO Auto-generated method stub
        TreeMap<Double, Location> treeMap = treeMapArray.get(deviceId);
		
		Entry<Double, Location> e = treeMap.floorEntry(time);
	    
	    if(e == null){
	    	SimLogger.printLine("impossible is occurred! no location is found for the device '" + deviceId + "' at " + time);
	    	System.exit(1);
	    }
	    
		return e.getValue();
    }
    
}
