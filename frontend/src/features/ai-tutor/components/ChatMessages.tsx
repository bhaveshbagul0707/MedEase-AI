import { useEffect, useRef } from "react";

import type { ChatMessage as Message } from "../api";
import ChatMessage from "./ChatMessage";

interface ChatMessagesProps {
    messages: Message[];
    isLoading: boolean;
}

export default function ChatMessages({
    messages,
    isLoading,
}: ChatMessagesProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages]);

    if (isLoading) {
        return (
            <div className="flex flex-1 items-center justify-center">
                <p className="text-slate-500">
                    Loading conversation...
                </p>
            </div>
        );
    }

    if (messages.length === 0) {
        return (
            <div className="flex flex-1 items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold">
                        Start studying 🚀
                    </h2>

                    <p className="mt-2 text-slate-500">
                        Ask any medical question to begin.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="mx-auto max-w-4xl space-y-6">

                {messages.map((message) => (
                    <ChatMessage
                        key={message.id}
                        message={message}
                    />
                ))}

                <div ref={bottomRef} />

            </div>
        </div>
    );
}