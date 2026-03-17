"use client";

import { useState, KeyboardEvent, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { X } from "lucide-react";
import apiClient from "@/lib/api";
import { useSession } from "@/lib/auth-client";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  className?: string;
}

export function TagInput({ value = [], onChange, placeholder = "Add tags...", className }: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const { data: session } = useSession();

  useEffect(() => {
    // Fetch user's existing tags for autocomplete
    const fetchTags = async () => {
      if (session?.user?.id) {
        try {
          const res = await apiClient.get<string[]>(`/api/${session.user.id}/tags`);
          if (res.data && Array.isArray(res.data)) {
            setSuggestions(res.data);
          }
        } catch (error) {
          console.error("Failed to fetch tags", error);
        }
      }
    };
    fetchTags();
  }, [session?.user?.id]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === "Backspace" && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  };

  const addTag = (tag: string) => {
    const trimmed = tag.trim();
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
      setInputValue("");
    }
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const filteredSuggestions = suggestions.filter(
    s => !value.includes(s) && s.toLowerCase().includes(inputValue.toLowerCase())
  );

  return (
    <div className={className}>
      <div className="flex flex-wrap gap-2 mb-2">
        {value.map((tag) => (
          <Badge key={tag} variant="secondary" className="px-2 py-1 flex items-center gap-1">
            {tag}
            <button type="button" onClick={() => removeTag(tag)} className="ml-1 hover:text-destructive">
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
      </div>
      <div className="relative">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="bg-white/50 border-white/20 focus:border-primary/50"
        />
        {inputValue && filteredSuggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-popover border border-border rounded-md shadow-md max-h-40 overflow-y-auto">
            {filteredSuggestions.map(suggestion => (
              <div
                key={suggestion}
                className="px-3 py-2 cursor-pointer hover:bg-muted text-sm"
                onClick={() => {
                  addTag(suggestion);
                  setInputValue("");
                }}
              >
                {suggestion}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
