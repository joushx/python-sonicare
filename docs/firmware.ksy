meta:
  id: sonicare_upg
  title: Philips Sonicare firmware upgrade file (.upg)
  file-extension: upg
  endian: le
doc: |
  Checked against Oslo_v1.4.3.upg and Shanghai_v2.11.1.upg: in both the two
  records end exactly at the end of the file. Not checked with the Kaitai
  compiler, only with a python re-implementation of this layout.
seq:
  - id: magic
    contents: [0xfc, "UPH"]
  - id: reserved
    size: 4
    doc: ff ff ff ff
  - id: payload_size
    type: u4
    doc: file size - 72
  - id: header_version
    type: u2
    doc: always 1
  - id: signature_size
    type: u2
    doc: always 56
  - id: signature
    size: signature_size
    doc: high entropy, probably a signature or hash (not verified)
  - id: unknown_a
    type: u2
    doc: always 1
  - id: first_record_offset
    type: u2
    doc: 0x114, offset from the start of the file
  - id: record_count
    type: u4
    doc: 2 (boot2nd, main)
  - id: product
    type: strz
    size: 64
    encoding: ASCII
    doc: '"Philips Sonicare HX99XX"'
  - id: product_version
    type: strz
    size: 64
    encoding: ASCII
    doc: literally "product version", a template placeholder
  - id: component_name
    type: strz
    size: 64
    encoding: ASCII
    doc: literally "component name", a template placeholder
  - id: unknown_b
    type: u4
    doc: always 1
  - id: records
    type: record
    repeat: expr
    repeat-expr: record_count
types:
  record:
    seq:
      - id: length
        type: u4
        doc: length of the whole record, including this field and the trailer
      - id: name
        type: strz
        size: 8
        encoding: ASCII
      - id: data
        size: length - 16
        doc: starts with u4 1, no readable strings, looks encrypted or compressed
      - id: trailer
        type: u4
        doc: checksum or MAC; not a plain CRC32, Adler32 or byte sum of the data
