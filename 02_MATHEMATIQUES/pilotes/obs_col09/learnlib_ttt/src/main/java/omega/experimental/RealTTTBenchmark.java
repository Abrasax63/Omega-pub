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
import java.util.Random;
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

    static Word<String> findRandomCounterexample(
            Source source, MooreMachine<?, String, ?, String> hypothesis,
            List<String> alphabet, Random random, Meter meter) {
        String actualState = source.initial;
        List<String> word = new ArrayList<>();
        meter.eqResets++;
        meter.resets++;
        meter.check();
        for (int i = 0; i < 2000; i++) {
            if (random.nextDouble() <= 0.12) {
                word.clear();
                actualState = source.initial;
                meter.resets++;
                meter.eqResets++;
                meter.check();
            }
            String action = alphabet.get(random.nextInt(alphabet.size()));
            word.add(action);
            actualState = source.next.get(actualState).get(action);
            meter.symbols++;
            meter.eqSymbols++;
            meter.check();
            Word<String> input = Word.fromList(word);
            // MooreMachine's computeOutput includes the state after the last input.
            Word<String> predicted = hypothesis.computeOutput(input);
            String expected = source.outputs.get(actualState);
            if (!Objects.equals(predicted.lastSymbol(), expected)) {
                return input;
            }
        }
        return null;  // bounded random-walk oracle, not a proof of equivalence
    }

    static void runOne(String filename, Path dot, int index) throws Exception {
        Source target = Source.load(dot);
        List<String> symbols = new ArrayList<>(target.alphabet);
        Collections.sort(symbols);
        Alphabet<String> alphabet = Alphabets.fromList(symbols);
        Meter meter = new Meter();
        RealMembership membership = new RealMembership(target, meter);

        // This class comes from LearnLib, not from Omega.
        TTTLearnerMoore<String, String> learner =
            new TTTLearnerMoore<>(alphabet, membership, AcexAnalyzers.BINARY_SEARCH_BWD);

        Random random = new Random(20261115L + index);
        long cpuBefore = java.lang.management.ManagementFactory.getThreadMXBean()
                .getCurrentThreadCpuTime();
        long wallBefore = System.nanoTime();
        learner.startLearning();
        int rounds = 0;
        int cexs = 0;
        while (rounds++ < 40) {
            Word<String> counterexample =
                findRandomCounterexample(target, learner.getHypothesisModel(), symbols, random, meter);
            if (counterexample == null) break;
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

        Random evalRng = new Random(20261116L + index);
        int evalCount = 0;
        int errors = 0;
        for (int i = 0; i < 256; i++) {
            int len = 12 + evalRng.nextInt(7);
            List<String> sequence = new ArrayList<>();
            for (int j = 0; j < len; j++) {
                sequence.add(symbols.get(evalRng.nextInt(symbols.size())));
            }
            Word<String> input = Word.fromList(sequence);
            String expected = target.run(input).get(len);
            String predicted = learner.getHypothesisModel().computeOutput(input).lastSymbol();
            errors += !Objects.equals(expected, predicted) ? 1 : 0;
            evalCount++;
        }

        System.out.printf(
            "{\"fixture\":\"%s\",\"algorithm\":\"TTT-LearnLib-0.18.0\","
            + "\"true_states_posthoc\":%d,\"learned_states\":%d,"
            + "\"membership_queries\":%d,\"membership_symbols\":%d,"
            + "\"physical_resets\":%d,\"physical_symbols\":%d,"
            + "\"eq_resets\":%d,\"eq_symbols\":%d,\"cex_count\":%d,"
            + "\"heldout_total\":%d,\"heldout_errors\":%d,"
            + "\"cpu_ns\":%d,\"wall_ns\":%d,"
            + "\"equivalence_certified\":false,\"directly_comparable_to_aalpy\":false}%n",
            filename, target.outputs.size(), learner.getHypothesisModel().size(),
            meter.mqCount, meter.mqSymbols, meter.resets, meter.symbols,
            meter.eqResets, meter.eqSymbols, cexs, evalCount, errors,
            Math.max(0L, cpuAfter - cpuBefore), wallAfter - wallBefore
        );
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            throw new IllegalArgumentException("Pass path to external_fixtures directory");
        }
        Path folder = Path.of(args[0]);
        String[] names = {"Angluin_Moore.dot", "coffee_moore.dot", "mooreModel.dot"};
        for (int i = 0; i < names.length; i++) {
            runOne(names[i], folder.resolve(names[i]), i);
        }
    }
}
