import io, uuid

persi_stdout = None
persi_stderr = None

class _StreamOutputForwarderPartial(io.TextIOBase):
    def __init__(self
                , original_text_stream:io.TextIOBase
                , output_dict: dict):
      assert isinstance(original_text_stream, io.TextIOBase)
      assert isinstance(output_dict, dict)
      self.output_dict = output_dict
      self.original_stream = original_text_stream

    def write(self, message: str) -> int:
      message_name = str(uuid.uuid4())
      return_value = 0
      try:
          return_value = self.original_stream.write(message)
      except:
          pass
      self.output_dict[message_name] = message
      return return_value

    def writelines(self, lines):
        """Write a list of lines to the stream."""
        for line in lines:
            self.write(line)

class _StreamOutputForwarder(_StreamOutputForwarderPartial):
    def __init__(self,*args, **kwargs):
      super().__init__(*args, **kwargs)

    def __getattribute__(self, item):
      if item in ["original_stream","write","writelines","output_dict"]:
        return super().__getattribute__(item)
      return self.original_stream.__getattribute__(item)

    def __getattr__(self, item):
        return self._original_stream.__getattribute__(item)