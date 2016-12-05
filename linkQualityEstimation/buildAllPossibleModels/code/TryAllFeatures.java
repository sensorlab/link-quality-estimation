import weka.core.converters.ConverterUtils.DataSource;
import weka.core.Instances;
import weka.classifiers.Classifier;
import weka.classifiers.trees.J48;
import weka.filters.unsupervised.attribute.Remove;
import weka.classifiers.Evaluation;

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

import weka.filters.Filter;
import weka.filters.unsupervised.attribute.Remove;
import weka.core.Attribute;
import weka.filters.unsupervised.attribute.SortLabels;
import weka.filters.MultiFilter;

class MapUtil
{
    public static <K, V extends Comparable<? super V>> Map<K, V> 
        sortByValue( Map<K, V> map )
    {
        List<Map.Entry<K, V>> list =
            new LinkedList<Map.Entry<K, V>>( map.entrySet() );
        Collections.sort( list, new Comparator<Map.Entry<K, V>>()
        {
            public int compare( Map.Entry<K, V> o1, Map.Entry<K, V> o2 )
            {
                return (o1.getValue()).compareTo( o2.getValue() );
            }
        } );

        Map<K, V> result = new LinkedHashMap<K, V>();
        for (Map.Entry<K, V> entry : list)
        {
            result.put( entry.getKey(), entry.getValue() );
        }
        return result;
    }
}


public class TryAllFeatures {
	static final String FILENAME = "../dataset-10-JSI_sigfox_20161124.arff";
	static final List<String> unwantedAttributes = Arrays.asList("prr", "seq", "received", "attenuator", "link_num", "experiment_num", "pga_gain");

	public static Set<Set<Integer>> powerSet(Set<Integer> originalSet) {
		Set<Set<Integer>> sets = new HashSet<Set<Integer>>();
		if (originalSet.isEmpty()) {
			sets.add(new HashSet<Integer>());
			return sets;
		}
		List<Integer> list = new ArrayList<Integer>(originalSet);
		Integer head = list.get(0);
		Set<Integer> rest = new HashSet<Integer>(list.subList(1, list.size()));
		for (Set<Integer> set : powerSet(rest)) {
			Set<Integer> newSet = new HashSet<Integer>();
			newSet.add(head);
			newSet.addAll(set);
			sets.add(newSet);
			sets.add(set);
		}
		return sets;
	}

	public static int[] convertToArray(Set<Integer> set) {
		int[] retArray = new int[set.size()];
		int index = 0;
		for(Integer i : set) {
			retArray[index++] = i;
		}
		return retArray;
	}

	public static void main(String[] args) throws Exception {
		Set<Integer> attributeIndices = new HashSet<Integer>();
		Map<String, Float> allModels = new HashMap<String,Float>();
		Random rand = new Random(1);
		Remove removeUnwanted = new Remove();
		Remove removeOption = new Remove();
		DataSource source = new DataSource(FILENAME);
		Instances data = source.getDataSet();
		SortLabels sortLabels = new SortLabels();
		MultiFilter multiFilter = new MultiFilter();
		Filter[] filters;
		
		// get indices of unwanted attributes and class index
		String unwantedAttributesArgument = "";
		Attribute attribute;
		int numberOfAttributes = data.numAttributes();
		int numberOfUnwantedAttributes = 0;
		Integer classIndex = null;
		
		for(int attributeIndex = 0; attributeIndex < numberOfAttributes; attributeIndex++) {
			attribute = data.attribute(attributeIndex);
			if(attribute.name().equals("class")) {
				classIndex = attributeIndex + 1;
				continue;
			}
			if(unwantedAttributes.contains(attribute.name())) {
				numberOfUnwantedAttributes += 1;
				if(!unwantedAttributesArgument.equals(""))
					unwantedAttributesArgument += ",";
				unwantedAttributesArgument += Integer.toString(attributeIndex + 1);
			}
		}
		
		data.setClassIndex(classIndex - 1);
		
		sortLabels.setAttributeIndices(Integer.toString(classIndex));
		sortLabels.setInputFormat(data);
		
		removeUnwanted.setAttributeIndices(unwantedAttributesArgument); // starts at 1
		removeUnwanted.setInputFormat(data);
		
		removeOption.setInputFormat(data);

		// calculate all possible combinations of features (removal)
		IntStream.range(0, numberOfAttributes - numberOfUnwantedAttributes).forEach(n -> {
			attributeIndices.add(n);
		});
		
		int correctedClassIndex = classIndex - numberOfUnwantedAttributes;
		int maxSize = data.numAttributes() - numberOfUnwantedAttributes - 1;
		
		for(Set<Integer> option: powerSet(attributeIndices)) {
			if(option.contains(correctedClassIndex) || option.size() >= maxSize) {
				continue;
			}
			data = source.getDataSet();
			//TODO: doesn't always select the right class
			data.setClassIndex(classIndex - 1);
			

			// sort class names, remove unwanted attributes
			// remove attributes
			if(!option.isEmpty()) {
				filters = new Filter[3];
				removeOption.setAttributeIndicesArray(convertToArray(option));
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
			//System.out.println(option);
			for(int attributeIndex = 0; attributeIndex < data.numAttributes(); attributeIndex++) {
				attribute = data.attribute(attributeIndex);
				if(attribute.name().equals("class")) {
					continue;
				}
				usedAttributes += attribute.name() + " ";
			}
			System.out.println("Used attrs: " + usedAttributes);

			Classifier tree = new J48();
			tree.buildClassifier(data);
			
			// format output, only first 3 features in decision tree
			// TODO: fix, doesn't work correctly in all cases
			String bestThreeFeatures = "";
			String[] lines;
			try {
				String stringTree = tree.toString();
				lines = stringTree.split(System.getProperty("line.separator"));
				bestThreeFeatures += lines[3].split(" ")[0];
				//bestThreeFeatures += ", " + lines[4].split(" ")[3];
				//bestThreeFeatures += ", " + lines[5].split(" ")[6];
			}
			catch(Exception e) {
				System.out.println("------------------------------------------------");
			}
			System.out.println("Best three: " + bestThreeFeatures);
			
			Evaluation eval = new Evaluation(data);
			int folds = 10;
			eval.crossValidateModel(tree, data, folds, rand);
			
			String confusionMatrix = eval.toMatrixString();
			//System.out.println(confusionMatrix);
			String summary = eval.toSummaryString();
			System.out.println(summary);
			lines = summary.split(System.getProperty("line.separator"));
			int lengthLine = lines[1].split(" ").length;
			int backtrack = 0;
			boolean success = false;
			Float correctlyClassified = null;
			
			while(!success) {
				try {
					correctlyClassified = Float.parseFloat(lines[1].split(" ")[lengthLine - backtrack]); // relative to size
					success = true;
				}
				catch(Exception e) {
					backtrack++;
				}
			}
			String key = "Used: " + usedAttributes + "\nTop of the tree: " + bestThreeFeatures + "\nCorrectly classified: " + correctlyClassified + "%\n" + confusionMatrix + "\n-------------------------------------------------------\n\n";
			allModels.put(key, correctlyClassified);
			try{
			    PrintWriter writer = new PrintWriter("../output/" + usedAttributes + ".txt", "UTF-8");
			    writer.println("Best: " + bestThreeFeatures);
			    writer.println(confusionMatrix);
			    writer.println(summary);
			    writer.println(tree);
			    writer.close();
			} catch (Exception e) {
			   System.out.println(e);
			}
		}
		allModels = MapUtil.sortByValue(allModels);
		ListIterator<String> iterator = new ArrayList<String>(allModels.keySet()).listIterator(allModels.size());
		PrintWriter writer = new PrintWriter(FILENAME + ".txt", "UTF-8");	    
		while (iterator.hasPrevious()) {
			String key = iterator.previous();
			writer.println(key);
		}
		writer.close();
	}
}
/*

J48 pruned tree
------------------

attenuator <= -30
|   snr_std <= 1.369551
|   |   snr_std <= 1.197226
*/