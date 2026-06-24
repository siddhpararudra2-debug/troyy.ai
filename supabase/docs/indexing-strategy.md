# Indexing Strategy
Personal Engineering OS

## Overview
Indexes are designed for optimal performance on Supabase Free Tier.

## Core Indexes
| Table | Column | Index Type | Purpose |
|-------|--------|------------|---------|
| projects | status | B-tree | Filter projects by status |
| project_files | project_id | B-tree | Get all files for a project |
| artifacts | project_id | B-tree | Get all artifacts for a project |
| artifact_relationships | source_artifact_id, target_artifact_id | B-tree | Navigate relationships |
| parts | project_id, material_id | B-tree | Query parts by project and material |
| assemblies | project_id | B-tree | Query assemblies by project |
| simulations | project_id | B-tree | Get simulations for project |
| simulation_runs | simulation_id, status | B-tree | Filter runs by simulation and status |
| twins | project_id | B-tree | Get twins for project |
| telemetry_records | twin_id, timestamp | B-tree, DESC on timestamp | Efficient telemetry queries by time range |
| knowledge_nodes | node_type | B-tree | Filter nodes by type |
| knowledge_edges | source_node_id, target_node_id | B-tree | Navigate graph |
| document_embeddings | embedding | ivfflat (vector_cosine_ops) | Fast semantic search |

## Vector Search Indexes
For pgvector, we use ivfflat indexes for cosine similarity search:
- Indexed on vector columns with `vector_cosine_ops` operator class
- Optimized for 1536-dimensional embeddings (OpenAI ada-002 compatible)
- Build after loading initial data for best clustering

## Notes
- Indexes are created in schema.sql
- Additional indexes can be added based on usage patterns
- For very large telemetry tables, consider partitioning by time
