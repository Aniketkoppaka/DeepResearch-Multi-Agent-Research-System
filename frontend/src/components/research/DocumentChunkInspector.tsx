import React, { useState } from "react";
import { FileText, Layers, Hash, Sparkles, Search, BookOpen } from "lucide-react";

export type DocumentChunk = {
  id: string;
  chunkIndex: number;
  heading: string;
  content: string;
  charCount: number;
  tokensEstimate: number;
  keywords: string[];
};

export const SAMPLE_CHUNKS: DocumentChunk[] = [
  {
    id: "chk-1",
    chunkIndex: 0,
    heading: "Executive Summary",
    content:
      "This research document evaluates the transition from classical asymmetric cryptography to Post-Quantum Cryptography (PQC) and Quantum Key Distribution (QKD) across modern cloud systems.",
    charCount: 201,
    tokensEstimate: 38,
    keywords: ["cryptography", "post-quantum", "pqc", "qkd", "cloud"],
  },
  {
    id: "chk-2",
    chunkIndex: 1,
    heading: "1. NIST Standardization: ML-KEM and ML-DSA",
    content:
      "NIST finalized PQC standards in 2024, focusing on lattice-based algorithms including ML-KEM (Module-Lattice Key Encapsulation) and ML-DSA (Module-Lattice Digital Signature Algorithm). Organizations are advised to prioritize hybrid migration combining classical ECDH with ML-KEM-768.",
    charCount: 284,
    tokensEstimate: 54,
    keywords: ["nist", "ml-kem", "ml-dsa", "lattice", "hybrid", "ecdh"],
  },
  {
    id: "chk-3",
    chunkIndex: 2,
    heading: "2. Quantum Key Distribution Realities and Challenges",
    content:
      "QKD leverages quantum mechanics (BB84 protocols) over optical fiber and satellite links. While QKD provides information-theoretic security, distance limits (<100km in standard fiber) and trusted repeater node vulnerabilities remain major engineering bottlenecks.",
    charCount: 268,
    tokensEstimate: 51,
    keywords: ["qkd", "bb84", "fiber", "repeater", "bottlenecks", "quantum"],
  },
  {
    id: "chk-4",
    chunkIndex: 3,
    heading: "3. Recommended Enterprise Action Items",
    content:
      "1. Conduct an enterprise cryptographic inventory and establish algorithm agility frameworks. 2. Deploy hybrid TLS 1.3 key exchange (X25519 + ML-KEM) on edge gateways and microservices. 3. Audit data retention policies against Store-Now-Decrypt-Later (SNDL) adversary attacks.",
    charCount: 279,
    tokensEstimate: 53,
    keywords: ["agility", "tls", "x25519", "ml-kem", "sndl", "inventory"],
  },
];

type Props = {
  documentName?: string;
  chunks?: DocumentChunk[];
};

export function DocumentChunkInspector({
  documentName = "sample_research_doc.pdf",
  chunks = SAMPLE_CHUNKS,
}: Props) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredChunks = chunks.filter(
    (c) =>
      c.heading.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.keywords.some((k) => k.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-4 text-xs">
      {/* File Ingestion Header Card */}
      <div className="rounded-xl border border-white/10 bg-[#212121] p-4">
        <div className="flex items-center gap-2.5">
          <div className="flex size-8 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">
            <FileText className="size-4" />
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="font-semibold text-white truncate">{documentName}</h4>
            <p className="text-[11px] text-neutral-400 mt-0.5">
              Semantic Boundary Splitting · {chunks.length} chunks indexed
            </p>
          </div>
        </div>

        <div className="mt-3 grid grid-cols-3 gap-2 border-t border-white/5 pt-3 text-center">
          <div className="rounded-lg bg-neutral-900/60 p-2">
            <span className="text-[10px] text-neutral-400 block">Total Chunks</span>
            <span className="font-mono text-xs font-bold text-emerald-400">
              {chunks.length}
            </span>
          </div>
          <div className="rounded-lg bg-neutral-900/60 p-2">
            <span className="text-[10px] text-neutral-400 block">Avg Chars/Chunk</span>
            <span className="font-mono text-xs font-bold text-white">
              {Math.round(
                chunks.reduce((acc, c) => acc + c.charCount, 0) / chunks.length
              )}
            </span>
          </div>
          <div className="rounded-lg bg-neutral-900/60 p-2">
            <span className="text-[10px] text-neutral-400 block">Vector Index</span>
            <span className="font-mono text-xs font-bold text-cyan-400">
              Qdrant RRF
            </span>
          </div>
        </div>
      </div>

      {/* Search & Filter */}
      <div className="flex items-center gap-2 rounded-xl bg-neutral-900 border border-white/10 px-3 py-1.5">
        <Search className="size-3.5 text-neutral-400" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Filter semantic chunks or keywords…"
          className="w-full bg-transparent text-xs text-white outline-none placeholder:text-neutral-500"
        />
      </div>

      {/* Chunk List */}
      <div className="space-y-3">
        {filteredChunks.map((chunk) => (
          <div
            key={chunk.id}
            className="rounded-xl border border-white/10 bg-[#212121] p-3.5 space-y-2 hover:border-emerald-500/30 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 font-medium text-emerald-400 text-[11px]">
                <BookOpen className="size-3" />
                <span>{chunk.heading}</span>
              </div>
              <span className="rounded bg-neutral-800 px-1.5 py-0.5 font-mono text-[10px] text-neutral-400">
                Chunk #{chunk.chunkIndex}
              </span>
            </div>

            <p className="text-neutral-300 leading-relaxed text-xs">
              {chunk.content}
            </p>

            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-white/5 text-[10px] text-neutral-400">
              <div className="flex flex-wrap gap-1">
                {chunk.keywords.map((k) => (
                  <span
                    key={k}
                    className="rounded bg-neutral-900/80 px-1.5 py-0.5 text-neutral-300 border border-white/5"
                  >
                    #{k}
                  </span>
                ))}
              </div>
              <span className="font-mono">
                {chunk.charCount} chars · ~{chunk.tokensEstimate} tokens
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
