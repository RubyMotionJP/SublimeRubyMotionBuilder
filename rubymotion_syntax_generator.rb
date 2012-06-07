#!/usr/bin/env ruby -wKU

require "stringio"

DebugEnabled = true

ignore_files = [
  "Default.sublime-commands",
  "Default.sublime-keymap",
  "RubyMotion.sublime-build",
  "RubyMotion.sublime-settings"
]

Dir.foreach("../Ruby") do |file_name|

  src_file_name = "../Ruby/" + file_name
  if FileTest.file?(src_file_name)

    # skip cache files
    ext = File.extname(file_name)
    next if ext == ".cache"

    # Ruby.* rename to RubyMotion.*
    base = File.basename(file_name, ext) 
    base = "RubyMotion" if base == "Ruby"

    # skip ignore file
    next if ignore_files.include?(base + ext)

    dst_file_name = base + ext
    STDERR.puts "Creating: #{dst_file_name}" if DebugEnabled

    iobuf = StringIO.open

    File.open(src_file_name, "r") do |in_file|

      skip = false
      in_file.each do |line|
        # ignore lines
        skip = false if skip and line =~ /<key>/
        skip = true if line =~ />(fileTypes|firstLineMatch)</
        next if skip

        line = line.gsub(/>Ruby</, ">RubyMotion<")
        line = line.gsub(/source\.ruby/, "source.rubymotion")
        line = line.gsub(/\.ruby</, '.rubymotion<')
        line = line.gsub(/>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}</, ">#{`uuidgen`.chomp}<")

        iobuf.puts line

      end # in_file.each

    end # File.open of in_file

    File.open(dst_file_name, "w") do |out_file|
      out_file.puts iobuf.string
    end  # File.open of out_file

    iobuf.close

  end # file_name is file?

end # Dir.foreach
