import type { ChatMessage } from "../api";

interface ChatMessageProps {
    message: ChatMessage;
}

export default function ChatMessage({
    message,
}: ChatMessageProps) {
    const isUser = message.role === "user";

    return (
        <div
            className={`flex ${
                isUser ? "justify-end" : "justify-start"
            }`}
        >
            <div
                className={`max-w-3xl rounded-2xl px-5 py-4 shadow-sm ${
                    isUser
                        ? "bg-blue-600 text-white"
                        : "border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
                }`}
            >
                <div className="mb-2 flex items-center gap-2">
                    <span className="text-lg">
                        {isUser ? "👤" : "🤖"}
                    </span>

                    <span className="text-sm font-semibold">
                        {isUser ? "You" : "MedEase AI"}
                    </span>
                </div>

                <div className="whitespace-pre-wrap text-sm leading-7">
                    {message.content}
                </div>

                {!isUser && (
                    <div className="mt-4 flex gap-2">

                        <button
                            className="rounded-lg border px-3 py-1 text-xs hover:bg-slate-100 dark:hover:bg-slate-800"
                        >
                            📋 Copy
                        </button>

                        <button
                            className="rounded-lg border px-3 py-1 text-xs hover:bg-slate-100 dark:hover:bg-slate-800"
                        >
                            👍
                        </button>

                        <button
                            className="rounded-lg border px-3 py-1 text-xs hover:bg-slate-100 dark:hover:bg-slate-800"
                        >
                            👎
                        </button>

                    </div>
                )}
            </div>
        </div>
    );
}