import weka.core.converters.ConverterUtils.DataSource;
import weka.core.Instances;
import weka.classifiers.Classifier;
import weka.classifiers.trees.J48;
import weka.filters.unsupervised.attribute.Remove;
import weka.classifiers.Evaluation;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.Remove;
import weka.core.Attribute;
import weka.filters.unsupervised.attribute.SortLabels;
import weka.filters.MultiFilter;

import java.util.Arrays;
import java.util.Set;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.stream.IntStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Comparator;
import java.util.LinkedList;
import java.util.ListIterator;

import java.io.PrintWriter;


class Util {
	
	public static <K,V extends Comparable<? super V>> Map<K,V> sortMapByValue(Map<K,V> map) {
		List<Map.Entry<K,V>> list = new LinkedList<Map.Entry<K,V>>(map.entrySet());
		Collections.sort(list, new Comparator<Map.Entry<K,V>>() {
			public int compare(Map.Entry<K,V> o1, Map.Entry<K,V> o2) {
				return (o1.getValue()).compareTo(o2.getValue());
			}
		});

		Map<K,V> result = new LinkedHashMap<K,V>();
		for(Map.Entry<K,V> entry : list) {
			result.put(entry.getKey(), entry.getValue());
		}
		return result;
	}

	public static Set<Set<Integer>> powerSet(Set<Integer> originalSet) {
		Set<Set<Integer>> sets = new HashSet<Set<Integer>>();
		if (originalSet.isEmpty()) {
			sets.add(new HashSet<Integer>());
			return sets;
		}
		List<Integer> list = new ArrayList<Integer>(originalSet);
		Integer head = list.get(0);
		Set<Integer> rest = new HashSet<Integer>(list.subList(1, list.size()));
		for(Set<Integer> set : powerSet(rest)) {
			Set<Integer> newSet = new HashSet<Integer>();
			newSet.add(head);
			newSet.addAll(set);
			sets.add(newSet);
			sets.add(set);
		}
		return sets;
	}

	public static int[] convertSetToArray(Set<Integer> set) {
		int[] retArray = new int[set.size()];
		int index = 0;
		for(Integer i : set) {
			retArray[index++] = i;
		}
		return retArray;
	}
}


class WekaClassificationModelBuilder {

	String inputFileName;
	String outputDirectory;

	Set<Integer> attributeIndices;
	Map<String, Double> allModels;
	Random rand;
	Remove removeUnwanted;
	Remove removeOption;
	DataSource source;
	Instances data;
	SortLabels sortLabels;
	MultiFilter multiFilter;
	Filter[] filters;

	String unwantedAttributesArgument;
	Attribute attribute;
	int numberOfAttributes;
	int numberOfUnwantedAttributes;
	Integer classIndex;
	Integer numberOfUnwantedAttributesBeforeClass;
	List<String> unwantedAttributes;
	

	WekaClassificationModelBuilder(String inputFileName, String outputDirectory, List<String> unwantedAttributes) {
		
		this.inputFileName = inputFileName;
		this.outputDirectory = outputDirectory;
		this.unwantedAttributes = unwantedAttributes;

		attributeIndices = new HashSet<Integer>();
		rand = new Random(1);
		removeUnwanted = new Remove();
		removeOption = new Remove();
		try {
			source = new DataSource(inputFileName);
			data = source.getDataSet();
		}
		catch(Exception e) {
			e.printStackTrace(System.out);
			System.exit(1);
		}
		
		sortLabels = new SortLabels();
		multiFilter = new MultiFilter();
		
		unwantedAttributesArgument = "";
		numberOfAttributes = data.numAttributes();
		numberOfUnwantedAttributes = 0;
		classIndex = null;
		numberOfUnwantedAttributesBeforeClass = 0;

		setClassAndUnwanted();
	}


	private void setClassAndUnwanted() {
		
		for(int attributeIndex = 0; attributeIndex < numberOfAttributes; attributeIndex++) {
			attribute = data.attribute(attributeIndex);
			if(attribute.name().equals("class")) {
				classIndex = attributeIndex + 1;
				continue;
			}
			if(unwantedAttributes.contains(attribute.name())) {
				numberOfUnwantedAttributes += 1;
				if(classIndex == null)
					numberOfUnwantedAttributesBeforeClass += 1;
				if(!unwantedAttributesArgument.equals(""))
					unwantedAttributesArgument += ",";
				unwantedAttributesArgument += Integer.toString(attributeIndex + 1);
			}
		}

		if(classIndex == null) {
			System.out.println("Input file contains no attribute named 'class'!");
			System.exit(1);
		}
		
		data.setClassIndex(classIndex - 1);
		
		sortLabels.setAttributeIndices(Integer.toString(classIndex));		
		removeUnwanted.setAttributeIndices(unwantedAttributesArgument);
		
		try {
			sortLabels.setInputFormat(data);
			removeUnwanted.setInputFormat(data);
			removeOption.setInputFormat(data);
		}
		catch(Exception e) {
			e.printStackTrace(System.out);
			System.exit(1);
		}
	}
	

	public void buildAllModels(boolean outputToFile, Classifier cls, int folds) throws Exception {
		
		allModels = new HashMap<String,Double>();
		String topTreeFeature = "N/A";
		boolean isTree = false;

		if(J48.class.isInstance(cls)) {
			isTree = true;
		}
		
		// calculate all possible combinations of features (removal)
		IntStream.range(0, numberOfAttributes - numberOfUnwantedAttributes).forEach(n -> {
			attributeIndices.add(n);
		});
		
		// incorrect, attributes can also be after the class
		int correctedClassIndex = classIndex - (numberOfUnwantedAttributesBeforeClass + 1);
		int maxSize = data.numAttributes() - numberOfUnwantedAttributes - 1;
		
		for(Set<Integer> option: Util.powerSet(attributeIndices)) {

			if(option.contains(correctedClassIndex) || option.size() >= maxSize) {
				continue;
			}

			data = source.getDataSet();
			data.setClassIndex(classIndex - 1);

			// sort class names, remove unwanted attributes
			// remove attributes
			if(!option.isEmpty()) {
				filters = new Filter[3];
				removeOption.setAttributeIndicesArray(Util.convertSetToArray(option));
				filters[2] = removeOption;
			}
			else {
				filters = new Filter[2];
			}
			filters[0] = sortLabels;
			filters[1] = removeUnwanted;
			multiFilter.setFilters(filters);
			multiFilter.setInputFormat(data);
			data = Filter.useFilter(data, multiFilter);
			
			// print used attributes
			String usedAttributes = "";

			for(int attributeIndex = 0; attributeIndex < data.numAttributes(); attributeIndex++) {
				attribute = data.attribute(attributeIndex);
				if(attribute.name().equals("class")) {
					continue;
				}
				usedAttributes += attribute.name() + " ";
			}
			System.out.println("Used attrs: " + usedAttributes);

			cls.buildClassifier(data);
			

			if(isTree) {
				String[] topTreeSplit = ((J48)cls).prefix().split(System.getProperty("line.separator"))[0].split(":");
				if(topTreeSplit.length > 1 && topTreeSplit[0].length() > 0)
					topTreeFeature = topTreeSplit[0].substring(1);
				else	
					topTreeFeature = "N/A";

				System.out.println("Top of the tree: " + topTreeFeature);
			}
			

			Evaluation eval = new Evaluation(data);
			eval.crossValidateModel(cls, data, folds, rand);
			
			String confusionMatrix = eval.toMatrixString();
			String summary = eval.toSummaryString();
			Double correctlyClassified = eval.pctCorrect();


			String key = "Used: " + usedAttributes + "\nTop of the tree: " + topTreeFeature + "\nCorrectly classified: " +
				correctlyClassified + "%\n" + confusionMatrix + "\n-------------------------------------------------------\n\n";
			allModels.put(key, correctlyClassified);
			
			if(outputToFile) {
				try {
					PrintWriter writer = new PrintWriter("../output/" + usedAttributes + ".txt", "UTF-8");
					writer.println("Best: " + topTreeFeature);
					writer.println(confusionMatrix);
					writer.println(summary);
					writer.println(cls);
					writer.close();
				} catch (Exception e) {
					e.printStackTrace(System.out);
					System.exit(1);
				}
			}
		}
		
		allModels = Util.sortMapByValue(allModels);
	}
	

	public void listToFile() {
		ListIterator<String> iterator = new ArrayList<String>(allModels.keySet()).listIterator(allModels.size());
		PrintWriter writer = null;
		
		try {
			writer = new PrintWriter(inputFileName.substring(0, inputFileName.length() - 4) + "txt", "UTF-8");
		}
		catch(Exception e) {
			e.printStackTrace(System.out);
			System.exit(1);
		}
		
		while (iterator.hasPrevious()) {
			String key = iterator.previous();
			writer.println(key);
		}
		writer.close();
	}	
}


public class TryAllFeatures {
	static final String FILENAME = "../dataset-10-JSI_sigfox_20161124.arff";
	static final String OUTFILENAME = "../output";
	static final List<String> UNWANTEDATTRIBUTES = 
		Arrays.asList("prr", "seq", "received", "attenuator", "link_num", "experiment_num", "pga_gain");


	public static void main(String[] args) throws Exception {
		WekaClassificationModelBuilder wmb = new WekaClassificationModelBuilder(FILENAME, OUTFILENAME, UNWANTEDATTRIBUTES);

		wmb.buildAllModels(true, new J48(), 10);
		wmb.listToFile();
	}
}