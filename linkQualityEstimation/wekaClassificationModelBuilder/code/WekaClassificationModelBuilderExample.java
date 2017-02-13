/*
	This file contains a sample usage of WEKAClassificationModelBuilder.
*/

import java.util.Arrays;
import java.util.List;
import weka.classifiers.trees.J48;

/**
 * Test class for running WEKAClassificationModelBuilder.
 */
public class WekaClassificationModelBuilderExample {
	static final String FILENAME = "../dataset-10-JSI_sigfox_20161124.arff";
	static final String OUTFILENAME = "../output";
	static final List<String> UNWANTEDATTRIBUTES = 
		Arrays.asList("prr", "seq", "received", "attenuator", "link_num", "experiment_num", "pga_gain");

	/**
	 * Main method for testing WekaClassificationModelBuilder.
	 */
	public static void main(String[] args) throws Exception {
		WekaClassificationModelBuilder wmb = new WekaClassificationModelBuilder(FILENAME, OUTFILENAME, UNWANTEDATTRIBUTES);

		wmb.buildAllModels(true, new J48(), 10);
		wmb.listToFile();
	}
}