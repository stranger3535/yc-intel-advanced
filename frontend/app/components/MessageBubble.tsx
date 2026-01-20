type MessageBubbleProps = {
  role: "user" | "bot";
  text: string;
};

export default function MessageBubble({ role, text }: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={`max-w-[80%] px-4 py-2 rounded-lg ${
        isUser
          ? "ml-auto bg-blue-600 text-white"
          : "mr-auto bg-slate-800 text-green-300"
      }`}
    >
      <p className="text-sm whitespace-pre-wrap">{text}</p>
    </div>
  );
}
