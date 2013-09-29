#!/usr/bin/env ruby -wKU

require "stringio"
begin
  require 'zip'
rescue LoadError => e
  STDERR.puts 'rubyzip is required. Run "gem install rubyzip"'
end

DebugEnabled = true

ignore_files = [
  "RubyMotion.tmLanguage",
  "Default.sublime-commands",
  "Default.sublime-keymap",
  "RubyMotion.sublime-build",
  "RubyMotion.sublime-settings"
]

ruby_package_file = '/Applications/Sublime Text.app/Contents/MacOS/Packages/Ruby.sublime-package'

Zip::File.foreach(ruby_package_file) do |zip|
  next if zip.ftype != :file

  file_name = zip.name
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

  uuid = ">#{`uuidgen`.chomp}<"
  iobuf = StringIO.open

  begin
    tmpfile_path = "/tmp/#{file_name}"
    zip.extract(tmpfile_path)
    File.open(tmpfile_path, "r") do |in_file|

      skip = false
      in_file.each do |line|
        # ignore lines
        skip = false if skip and line =~ /<key>/
        skip = true if line =~ />(fileTypes|firstLineMatch)</
        next if skip

        line = line.gsub(/>Ruby</, ">RubyMotion<")
        line = line.gsub(/source\.ruby([< ])/, "source.rubymotion\\1")
        line = line.gsub(/>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}</, uuid)

        iobuf.puts line

      end # in_file.each

    end # File.open of in_file

    File.open(dst_file_name, "w") do |out_file|
      out_file.puts iobuf.string
    end  # File.open of out_file
  rescue
    STDERR.puts " -> FAILED: #{$!.backtrace.first} : #{$!}" if DebugEnabled

  ensure
    File.unlink(tmpfile_path) if File.exist?(tmpfile_path)
  end

  iobuf.close
end
