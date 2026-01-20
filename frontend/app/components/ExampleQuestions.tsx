const examples = [
  "Which YC companies work on AI?",
  "Fastest growing YC startups in 2024",
  "Which companies changed stage recently?",
  "Top AI startups by momentum score",
  "Which locations have the most new YC companies?"
];

export default function ExampleQuestions({
  onSelect,
}: {
  onSelect: (q: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {examples.map((q) => (
        <button
          key={q}
          onClick={() => onSelect(q)}
          className="px-3 py-1 text-sm rounded bg-slate-800 hover:bg-slate-700 text-slate-200"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
