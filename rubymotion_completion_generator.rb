#!/usr/bin/env ruby -wKU

require 'rexml/document'

DebugEnabled = true

# RubyMotion Bridgesupport default path
RubyMotionPath = ARGV[0] || "/Library/RubyMotion/data/5.1/BridgeSupport/"

STDERR.puts "build for " + RubyMotionPath if DebugEnabled

###############################################################

class JsonObject
  attr_reader :members

  def initialize(*_pairs)
    @members = []
    _pairs.each do |key, value|
      self[key] = value
    end
  end

  def eql?(_other)
    self.to_s.eql?(_other.to_s)
  end

  def hash
    self.to_s.hash
  end

  def [](_key)
    @members.assoc(_key.to_s)
  end

  def []=(_key, _value)
    key = _key.to_s
    pair = @members.assoc(key)
    if pair
      pair[1] = _value
    else
      @members << [key, _value]
    end

    return self
  end

  def to_json
    pairs_to_json(self.members, 0)
  end
  alias :to_s :to_json

  private

  def indent(_nest)
    ("  " * _nest)
  end

  def object_to_json(_object, _nest)
    if _object.is_a?(self.class)
      string = pairs_to_json(_object.members, _nest)
    elsif _object.is_a?(Array)
      string = array_to_json(_object, _nest)
    elsif _object.is_a?(String)
      string = string_to_json(_object, _nest)
    elsif _object.is_a?(Numeric)
      string = numeric_to_json(_object, _nest)
    elsif _object.nil?
      string = "null"
    elsif _object == true
      string = "true"
    elsif _object == false
      string = "false"
    else
      raise
    end

    return string
  end

  def pairs_to_json(_keyValuePairs, _nest)
    if _keyValuePairs.empty?
      string = "{ }"
    else
      string = "{\n#{indent(_nest + 1)}" + _keyValuePairs.collect {|key, value|
        pair_to_json(key, value, _nest + 1)
      }.join(",\n#{indent(_nest + 1)}") + "\n#{indent(_nest)}}"
    end

    return string
  end

  def array_to_json(_array, _nest)
    if _array.empty?
      string = "[ ]"
    else
      string = "[\n#{indent(_nest + 1)}" + _array.collect {|object|
        object_to_json(object, _nest + 1)
      }.join(",\n#{indent(_nest + 1)}") + "\n#{indent(_nest)}]"
    end

    return string
  end

  def string_to_json(_string, _nest)
    "\"#{_string}\""
  end

  def numeric_to_json(_numeric, _nest)
    _numeric.to_s
  end

  def pair_to_json(_key, _value, _nest)
    "#{string_to_json(_key, 0)}: #{object_to_json(_value, _nest)}"
  end

end

###############################################################

class RubyMotionCompletion
  def initialize(_dir)
    @_dir = _dir
  end

  # Compile the RubyMotion completion plist
  def compile
    # Load the directory entries
    if File.directory?(@_dir)

      completions = []

      Dir.foreach(@_dir) do |x|

        if x[0, 1] != '.'

          file = File.open(@_dir + x)
          doc = REXML::Document.new(file)

          if doc.root.has_elements?

            STDERR.puts("Compiling: %s" % x) if DebugEnabled

            doc.root.each_element do |node|
              case node.name
              when "class", "informal_protocol"
                completions += self.parse_class(node)
              when "function"
                completions += self.parse_function(node)
              when "function_alias"
                completions += self.parse_alias(node)
              when "constant"
                completions += self.parse_constant(node)
              when "string_constant"
                completions += self.parse_string(node)
              when "enum"
                completions += self.parse_enum(node)
              when "struct"
                # <TODO>
              when "cftype"
                # <TODO>
              when "opaque"
                # <TODO>
              else
                STDERR.puts "Unknown node #{node.name}"
              end
            end
          end
        end
      end

      # Output results
      STDERR.print("Sorting ...") if DebugEnabled

      jobj = JsonObject.new
      jobj["scope"] = "source.rubymotion"
      jobj["completions"] = completions.uniq.sort { |x, y| x.to_s <=> y.to_s }

      STDERR.puts(" done") if DebugEnabled

      return jobj.to_json
    end
  end

  # Create a completion string
  def create_completion(_trigger, _contents)
    if _trigger == _contents
      completion = _trigger
    else
      completion = JsonObject.new(["trigger", _trigger], ["contents", _contents])
    end

    return completion
  end

  # Create a contents string of a completion
  def create_contents(_method_name, _method)
    labels = _method_name.split(":")

    index = 0
    arguments = []

    # Create the arguments array
    _method.each_element("arg") do |arg|
      # Add argument to the array
      if index != 0 and labels[index]
        arguments << "%s:${%d:%s %s}" % [labels[index], (index + 1), arg.attribute("declared_type").to_s, arg.attribute("name").to_s]
      else
        arguments << "${%d:%s %s}" % [(index + 1), arg.attribute("declared_type").to_s, arg.attribute("name").to_s ]
      end
      index += 1
    end
    
    # Construct contents string
    contents = labels.first
    contents += "(%s)" % arguments.join(", ") unless arguments.empty?
    
    return contents 
  end

  # Returns a valid class definition
  def parse_class(_node)
    class_name = _node.attribute("name").to_s
    completions = [create_completion(class_name, class_name)]

    # Traverse class methods
    _node.each_element("method") do |method|
      # Prepend method name with class name if this is a class method
      method_name = method.attribute("selector").to_s
      method_name = "%s.%s" % [class_name, method_name] if method.attribute("class_method")

      trigger = method_name
      contents = create_contents(method_name, method)

      completions << create_completion(trigger, contents)
    end
    
    return completions
  end

  # Returns a valid function definition
  def parse_function(_node)
    function_name = _node.attribute("name").to_s

    trigger = function_name
    contents = create_contents(function_name, _node)

    return [create_completion(trigger, contents)]
  end

  # Returns a valid function_alias definition
  def parse_alias(_node)
    alias_name = _node.attribute("name").to_s
    alias_original = _node.attribute("original").to_s

    trigger = "%s (%s)" % [alias_name, alias_original]
    contents = alias_name

    return [create_completion(trigger, contents)]
  end

  # Returns a valid constant definition
  def parse_constant(_node)
    const_name = _node.attribute("name").to_s
    const_type = _node.attribute("declared_type").to_s

    # Make sure the first letter is always uppercase, for RubyMotion
    contents = "%s%s" % [const_name[0, 1].upcase, const_name[1..-1]]
    trigger = "%s (%s)" % [const_name, const_type]

    return [create_completion(trigger, contents)]
  end

  # Returns a valid string_constant definition
  def parse_string(_node)
    string_name = _node.attribute("name").to_s
    string_value = _node.attribute("value").to_s

    # Make sure the first letter is always uppercase, for RubyMotion
    contents = "%s%s" % [string_name[0, 1].upcase, string_name[1..-1]]
    trigger = "%s (%s)" % [string_name, string_value]

    return [create_completion(trigger, contents)]
  end

  # Returns a valid enum definition
  def parse_enum(_node)
    enum_name = _node.attribute( "name" ).to_s
    enum_value = _node.attribute( "value" ).to_s

    # Make sure the first letter is always uppercase, for RubyMotion
    contents = "%s%s" % [enum_name[0, 1].upcase, enum_name[1..-1]]
    trigger = "%s (%s)" % [enum_name, enum_value]

    return [create_completion(trigger, contents)]
  end

end

###############################################################

# Compile the completion tags
File.open("RubyMotion.sublime-completions", "w") do |file|
  file.puts RubyMotionCompletion.new(RubyMotionPath).compile
end