# Supabase Storage Architecture
Personal Engineering OS

## Buckets
The following buckets are configured:

| Bucket Name | Purpose | File Types |
|-------------|---------|------------|
| `cad-files` | Mechanical CAD models | .step, .stl, .f3d, .sldprt, .sldasm, etc. |
| `pcb-files` | Electrical design files | .kicad_pcb, .kicad_sch, .brd, .sch, etc. |
| `simulation-files` | Simulation data and results | .vtk, .stl, .csv, .json, etc. |
| `research-files` | Research papers, patents, standards | .pdf, .docx, .md, etc. |
| `manufacturing-files` | Manufacturing files | .gcode, .stl, .nc, gerbers, etc. |
| `reports` | Reports and documents | .pdf, .docx, .md, etc. |
| `documents` | General project documents | .pdf, .docx, .md, .txt, etc. |
| `telemetry` | Telemetry data | .csv, .json, .bin, etc. |

## Security
- All buckets use private access (no public URLs)
- Single user access only (same as database RLS)
- Files are organized by project ID

## File Organization
Example file paths:
```
cad-files/{project-id}/{part-id}/{version}/part.step
pcb-files/{project-id}/{pcb-id}/{revision}/board.kicad_pcb
research-files/{project-id}/{paper-id}/paper.pdf
telemetry/{twin-id}/{year}/{month}/{day}/{timestamp}.json
```
