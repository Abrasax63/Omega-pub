package omega.experimental;

import de.learnlib.algorithm.ttt.moore.TTTLearnerMoore;
import de.learnlib.acex.AcexAnalyzers;
import de.learnlib.oracle.MembershipOracle;
import de.learnlib.query.DefaultQuery;
import de.learnlib.query.Query;
import net.automatalib.alphabet.Alphabet;
import net.automatalib.alphabet.impl.Alphabets;
import net.automatalib.word.Word;
import net.automatalib.automaton.transducer.MooreMachine;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Genuine LearnLib TTTLearnerMoore 0.18.0, never a locally rewritten "TTT".
 * The published AALpy DOT target is passed only to the simulator membership
 * oracle. No true-state count / perfect equivalence oracle is made available
 * to the algorithm. EQ uses approximate random walks, so these costs MUST NOT
 * be compared as a fair ranking to AALpy's differently seeded Python oracle.
 */
public final class RealTTTBenchmark {
    private static final Pattern NODE = Pattern.compile(
            "^\\s*([A-Za-z0-9_]+)\\s*\\[(.*?)\\]\\s*;?\\s*$");
    private static final Pattern EDGE = Pattern.compile(
            "^\\s*([A-Za-z0-9_]+)\\s*->\\s*([A-Za-z0-9_]+)(?:\\s*\\[(.*?)\\])?\\s*;?\\s*$");
    private static final Pattern LABEL = Pattern.compile(
            "label\\s*=\\s*(?:\\\"([^\\\"]*)\\\"|([^,\\s\\]]+))");

    static final class Source {
        String initial;
        final Map<String, String> outputs = new LinkedHashMap<>();
        final Map<String, Map<String, String>> next = new LinkedHashMap<>();
        final Set<String> alphabet = new LinkedHashSet<>();

        static Source load(Path path) throws Exception {
            Source model = new Source();
            for (String line : Files.readAllLines(path)) {
                Matcher edge = EDGE.matcher(line);
                if (edge.matches()) {
                    String from = edge.group(1);
                    String to = edge.group(2);
                    if ("__start0".equals(from)) {
                        model.initial = to;
                        continue;
                    }
                    String input = labelValue(edge.group(3));
                    if (input == null || input.isEmpty()) {
                        throw new IllegalArgumentException("Missing transition label: " + line);
                    }
                    model.alphabet.add(input);
                    model.next.computeIfAbsent(from, k -> new LinkedHashMap<>()).put(input, to);
                    continue;
                }
                Matcher node = NODE.matcher(line);
                if (node.matches() && !"__start0".equals(node.group(1))) {
                    String label = labelValue(node.group(2));
                    if (label == null || !label.contains("|")) {
                        throw new IllegalArgumentException("Missing Moore output label: " + line);
                    }
                    String output = label.substring(label.lastIndexOf("|") + 1)
                            .replace("}", "").trim();
                    model.outputs.put(node.group(1), output);
                }
            }
            if (model.initial == null || model.outputs.isEmpty() || model.alphabet.isEmpty()) {
                throw new IllegalArgumentException("Incomplete external DOT " + path);
            }
            for (String state : model.outputs.keySet()) {
                Map<String, String> transitions = model.next.get(state);
                if (transitions == null || !transitions.keySet().containsAll(model.alphabet)) {
                    throw new IllegalArgumentException("Incomplete transitions from " + state);
                }
                for (String target : transitions.values()) {
                    if (!model.outputs.containsKey(target)) {
                        throw new IllegalArgumentException("Unknown successor " + target);
                    }
                }
            }
            return model;
        }

        static String labelValue(String attributes) {
            if (attributes == null) return null;
            Matcher m = LABEL.matcher(attributes);
            return m.find() ? (m.group(1) != null ? m.group(1) : m.group(2)) : null;
        }

        List<String> run(Word<String> input) {
            String state = initial;
            List<String> out = new ArrayList<>();
            out.add(outputs.get(state));
            for (String letter : input) {
                state = next.get(state).get(letter);
                out.add(outputs.get(state));
            }
            return out;
        }
    }

    static final class Meter {
        long resets = 0;
        long symbols = 0;
        long mqCount = 0;
        long mqSymbols = 0;
        long eqResets = 0;
        long eqSymbols = 0;
        final Set<List<String>> observedPrefixes = new LinkedHashSet<>();
        void check() {
            if (resets > 10000 || symbols > 50000) {
                throw new IllegalStateException("Physical query budget exceeded");
            }
        }
    }

    static final class RealMembership implements MembershipOracle.MooreMembershipOracle<String, String> {
        private final Source source;
        private final Meter meter;

        RealMembership(Source source, Meter meter) {
            this.source = source;
            this.meter = meter;
        }

        @Override
        public void processQueries(Collection<? extends Query<String, Word<String>>> queries) {
            for (Query<String, Word<String>> query : queries) {
                Word<String> full = query.getInput();
                int prefix = query.getPrefix().length();
                int suffix = query.getSuffix().length();
                List<String> outputs = source.run(full);
                List<String> prefixSeen = new ArrayList<>();
                for (String input : full) {
                    prefixSeen.add(input);
                    meter.observedPrefixes.add(List.copyOf(prefixSeen));
                }
                Word<String> response = Word.fromList(
                    outputs.subList(prefix, prefix + suffix + 1));
                meter.resets++;
                meter.symbols += full.length();
                meter.mqCount++;
                meter.mqSymbols += full.length();
                meter.check();
                query.answer(response);
            }
        }
    }

    /** Same fixed 512 candidate words as Python; first differing OUTPUT PREFIX wins. */
    static final class EqCounter {
        int rounds = 0;
        int proposedWords = 0;
        int counterexamples = 0;
        int completedSuites = 0;
    }

    static Word<String> findSharedCounterexample(
            Source source, MooreMachine<?, String, ?, String> hypothesis,
            List<List<String>> eqWords, Meter meter, EqCounter counter) {
        counter.rounds++;
        for (List<String> word : eqWords) {
            String actualState = source.initial;
            List<String> prefix = new ArrayList<>();
            meter.eqResets++;
            meter.resets++;
            counter.proposedWords++;
            meter.check();
            for (String action : word) {
                prefix.add(action);
                actualState = source.next.get(actualState).get(action);
                meter.symbols++;
                meter.eqSymbols++;
                meter.check();
                meter.observedPrefixes.add(List.copyOf(prefix));
                // Moore output after current prefix, like AALpy .step().
                String prediction = hypothesis.computeOutput(
                        Word.fromList(prefix)).lastSymbol();
                String observation = source.outputs.get(actualState);
                if (!Objects.equals(prediction, observation)) {
                    counter.counterexamples++;
                    return Word.fromList(prefix);
                }
            }
        }
        counter.completedSuites++;
        return null; // bounded common EQ test suite, NOT universal equivalence
    }

    static String sha256(Path path) throws Exception {
        MessageDigest dig = MessageDigest.getInstance("SHA-256");
        return HexFormat.of().formatHex(dig.digest(Files.readAllBytes(path)));
    }

    static List<List<String>> readManifest(Path path) throws Exception {
        List<List<String>> result = new ArrayList<>();
        Set<List<String>> unique = new LinkedHashSet<>();
        for (String line : Files.readAllLines(path)) {
            if (line.isBlank()) throw new IllegalArgumentException("Blank EQ word");
            List<String> word = List.of(line.split("\\t"));
            if (!unique.add(word)) {
                throw new IllegalArgumentException("Duplicate EQ word");
            }
            result.add(word);
        }
        if (result.size() != 512) throw new IllegalArgumentException("Expected 512 EQ words");
        return result;
    }

    static void runOne(String filename, Path dot, int index, Path matchedEvalDir) throws Exception {
        Source target = Source.load(dot);
        List<String> symbols = new ArrayList<>(target.alphabet);
        Collections.sort(symbols);
        Alphabet<String> alphabet = Alphabets.fromList(symbols);
        Meter meter = new Meter();
        RealMembership membership = new RealMembership(target, meter);

        // This class comes from LearnLib, not from Omega.
        TTTLearnerMoore<String, String> learner =
            new TTTLearnerMoore<>(alphabet, membership, AcexAnalyzers.BINARY_SEARCH_BWD);

        Path eqPath = matchedEvalDir.resolve(filename + ".eq.words");
        List<List<String>> eqWords = readManifest(eqPath);
        for (List<String> word : eqWords) {
            if (!symbols.containsAll(word)) throw new IllegalArgumentException("Invalid EQ symbol");
        }
        String eqSha = sha256(eqPath);
        String evalSha = sha256(matchedEvalDir.resolve(filename + ".words"));
        EqCounter eqCounter = new EqCounter();
        long cpuBefore = java.lang.management.ManagementFactory.getThreadMXBean()
                .getCurrentThreadCpuTime();
        long wallBefore = System.nanoTime();
        learner.startLearning();
        int rounds = 0;
        int cexs = 0;
        boolean suiteCompleted = false;
        while (rounds++ < 40) {
            Word<String> counterexample =
                findSharedCounterexample(target, learner.getHypothesisModel(), eqWords, meter, eqCounter);
            if (counterexample == null) {
                suiteCompleted = true;
                break;
            }
            cexs++;
            List<String> allOutputs = target.run(counterexample);
            // Moore output includes the initial state's output.
            DefaultQuery<String, Word<String>> query =
                new DefaultQuery<>(Word.epsilon(), counterexample, Word.fromList(allOutputs));
            boolean refined = learner.refineHypothesis(query);
            if (!refined) {
                throw new AssertionError("TTT did not refine on observed counterexample");
            }
        }
        long cpuAfter = java.lang.management.ManagementFactory.getThreadMXBean()
                .getCurrentThreadCpuTime();
        long wallAfter = System.nanoTime();

        List<String> testLines = Files.readAllLines(matchedEvalDir.resolve(filename + ".words"));
        Set<List<String>> uniqueTests = new LinkedHashSet<>();
        int evalCount = 0;
        int errors = 0;
        int unseenScored = 0;
        int unseenErrors = 0;
        int seenOverlap = 0;
        for (String line : testLines) {
            if (line.isBlank()) throw new IllegalArgumentException("Empty test word");
            List<String> sequence = List.of(line.split("\\t"));
            if (!uniqueTests.add(sequence)) throw new IllegalArgumentException("Repeated evaluation word");
            if (!symbols.containsAll(sequence)) throw new IllegalArgumentException("Foreign evaluation symbol");
            Word<String> input = Word.fromList(sequence);
            String expected = target.run(input).get(sequence.size());
            String predicted = learner.getHypothesisModel().computeOutput(input).lastSymbol();
            boolean error = !Objects.equals(expected, predicted);
            errors += error ? 1 : 0;
            boolean overlap = meter.observedPrefixes.contains(sequence);
            if (overlap) {
                seenOverlap++;
            } else {
                unseenScored++;
                unseenErrors += error ? 1 : 0;
            }
            evalCount++;
        }
        if (evalCount != 256 || unseenScored + seenOverlap != 256) {
            throw new AssertionError("Invalid matched evaluation manifest");
        }

        System.out.printf(
            "{\"fixture\":\"%s\",\"algorithm\":\"TTT-LearnLib-0.18.0\","
            + "\"eq_manifest_sha256\":\"%s\",\"evaluation_manifest_sha256\":\"%s\","
            + "\"eq_candidates_per_round\":512,\"eq_rounds\":%d,"
            + "\"eq_candidates_executed\":%d,\"eq_counterexamples\":%d,"
            + "\"completed_eq_suites\":%d,\"suite_completed\":%b,"
            + "\"true_states_posthoc\":%d,\"learned_states\":%d,"
            + "\"membership_queries\":%d,\"membership_symbols\":%d,"
            + "\"physical_resets\":%d,\"physical_symbols\":%d,"
            + "\"eq_resets\":%d,\"eq_symbols\":%d,\"cex_count\":%d,"
            + "\"heldout_total\":%d,\"heldout_errors\":%d,"
            + "\"heldout_overlap_seen_during_training\":%d,"
            + "\"heldout_unseen_scored\":%d,\"heldout_errors_unseen\":%d,"
            + "\"cpu_ns\":%d,\"wall_ns\":%d,"
            + "\"equivalence_certified\":false,\"directly_comparable_eq_protocol\":true}%n",
            filename, eqSha, evalSha,
            eqCounter.rounds, eqCounter.proposedWords, eqCounter.counterexamples,
            eqCounter.completedSuites, suiteCompleted,
            target.outputs.size(), learner.getHypothesisModel().size(),
            meter.mqCount, meter.mqSymbols, meter.resets, meter.symbols,
            meter.eqResets, meter.eqSymbols, cexs, evalCount, errors,
            seenOverlap, unseenScored, unseenErrors,
            Math.max(0L, cpuAfter - cpuBefore), wallAfter - wallBefore
        );
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            throw new IllegalArgumentException("Pass fixture directory and matched evaluation directory");
        }
        Path folder = Path.of(args[0]);
        Path evalDir = Path.of(args[1]);
        String[] names = {"Angluin_Moore.dot", "coffee_moore.dot", "mooreModel.dot"};
        for (int i = 0; i < names.length; i++) {
            runOne(names[i], folder.resolve(names[i]), i, evalDir);
        }
    }
}
