from . import MFRC522

class WriteRequest:
    def __init__(self, blocknum:int, data:list[int]) -> None:
        if len(data) != 16: raise ValueError("data length has to be 16!")
        if blocknum < 0 or blocknum >= 64: raise ValueError("Bad Block Number")
        self.blocknum = blocknum
        self.data = bytearray(data)
        pass

class RawMFRC522:
    """
    A class for reading, writing and clearing data using the MFRC522 RFID module with extended function.

    Attributes:
        MFRC522 (module): The MFRC522 module used for communication with the RFID reader.
        KEY (list): The default authentication key used for reading and writing data.
    """
    def __init__(self, KEY=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]):
        """
        Initializes a BasicMFRC522 instance.

        Args:
            KEY (list): The authentication key used for reading and writing data.
        """
        self.MFRC522 = MFRC522()  # Create an instance of the MFRC522 class
        self.KEY = KEY  # Set the authentication key

    def read_sector(self, trailer_block):
        """
        Read data from a sector of the RFID tag.

        Args:
            trailer_block (int): The block number of the sector trailer.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data read (as a string).
        """
        id, text = self.read_no_block(trailer_block)
        while not id:
            id, text = self.read_no_block(trailer_block)
        return id, text
    
    def read_sector_times(self, trailer_block, key, max_try):
        """
        Read data from a sector of the RFID tag.

        Args:
            trailer_block (int): The block number of the sector trailer.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data read (as a string).
        """
        id, text = self.read_no_block(trailer_block)
        self.KEY = key
        count = 1
        while not text:
            self.MFRC522.Init()
            id, text = self.read_no_block(trailer_block)
            count += 1
            if (count == max_try): 
                self.KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                return None, None, count
        self.KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        return id, text, count

    def read_sectors(self, trailer_blocks):
        """
        Read data from multiple sectors of the RFID tag.

        Args:
            trailer_blocks (list): The list of block numbers of the sector trailers.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the concatenated data read from all sectors (as a string).
        """
        text_all = ''
        for trailer_block in trailer_blocks:
            id, text = self.read_sector(trailer_block)
            text_all += text
        return id, text_all

    def read_id(self):
        """
        Read the tag ID from the RFID tag.

        Returns:
            int: The tag ID as an integer.
        """
        id = self.read_id_no_block()
        while not id:
            id = self.read_id_no_block()
        return id

    def read_id_no_block(self):
        """
        Attempt to read the tag ID from the RFID tag.

        Returns:
            int: The tag ID as an integer, or None if the operation fails.
        """
        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None

        # Anticollision, return UID if successful
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None

        # Convert UID to integer and return as the tag ID
        return self._uid_to_num(uid)

    def read_no_block(self, trailer_block):
        """
        Attempt to read data from the RFID tag.

        Args:
            trailer_block (int): The block number of the sector trailer.
            block_addr (tuple): The block numbers of the data blocks to read.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data read (as a string),
                or (None, None) if the operation fails.
        """
        if not self._check_trailer_block(trailer_block):
            raise ValueError("Invalid Trailer Block {trailer_block}")

        block_addr = (trailer_block-3, trailer_block-2, trailer_block-1, trailer_block) #Include Self!

        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None

        # Anticollision, return UID if successful
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None

        # Convert UID to integer and store as the tag ID
        id = self._uid_to_num(uid)

        # Select the RFID tag
        self.MFRC522.SelectTag(uid)

        # Authenticate with the tag using the provided key
        status = self.MFRC522.Authenticate(self.MFRC522.PICC_AUTHENT1A, trailer_block, self.KEY, uid)

        # Initialize variables for storing data and text read from the tag
        data = []
        raw_data = None

        try:
            if status == self.MFRC522.MI_OK:
                # Read data blocks specified by block_addr
                for block_num in block_addr:
                    block = self.MFRC522.ReadTag(block_num)
                    if block:
                        data += block

                # Convert data to string
                if data:
                    raw_data = data #return raw binaries

            # Stop cryptographic communication with the tag
            self.MFRC522.StopCrypto1()

            # Return the tag ID and the read data
            return id, raw_data

        except:
            # Stop cryptographic communication with the tag in case of exception
            self.MFRC522.StopCrypto1()

            # Return None, None if an exception occurs
            return None, None
        
    def write_sector(self, text, trailer_block):
        """
        Write data to a sector of the RFID tag.

        Args:
            text (str): The data to write.
            trailer_block (int): The block number of the sector trailer.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data written (as a string).
        """

        # Write the data to the RFID tag using the helper function write_no_block
        id, text_in = self.write_no_block(text, trailer_block)

        # Retry writing if it fails initially
        while not id:
            id, text_in = self.write_no_block(text, trailer_block)

        # Return the tag ID and the written data
        return id, text_in

    def write_sectors(self, text, trailer_blocks):
        """
        Write data to multiple sectors of the RFID tag.

        Args:
            text (str): The data to write.
            trailer_blocks (list): The list of block numbers of the sector trailers.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the concatenated data written to all sectors (as a string).
        """
        # Split the input text into chunks of 48 characters
        text_formated_list = self._split_string(text)

        # Initialize an empty string to store the concatenated data
        text_all = ''

        # Iterate through the trailer_blocks list
        for i in range(0, len(trailer_blocks)):
            try:
                # Write data to the sector using the write_sector function
                id, text = self.write_sector(text_formated_list[i], trailer_blocks[i])

                # Concatenate the written data to the text_all string
                text_all += text
            except IndexError:
                # Ignore any index errors that may occur if there are fewer chunks than trailer blocks
                pass

        # Return the tag ID and the concatenated data
        return id, text_all

    def write_no_block(self, text, trailer_block):
        """
        Attempt to write data to the RFID tag.

        Args:
            text (str): The data to write.
            trailer_block (int): The block number of the sector trailer.
            block_addr (tuple): The block numbers of the data blocks to write.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data written (as a string), or (None, None) if the operation fails.
        """
        if not self._check_trailer_block(trailer_block):
            raise ValueError("Invalid Trailer Block {trailer_block}")

        block_addr = (trailer_block-3, trailer_block-2, trailer_block-1)
        text = str(text)

        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None

        # Anticollision, return UID if success
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None

        # Convert UID to integer and store as id
        id = self._uid_to_num(uid)

        # Select the RFID tag using the UID
        self.MFRC522.SelectTag(uid)

        # Authenticate with the sector trailer block using the default key
        status = self.MFRC522.Authenticate(self.MFRC522.PICC_AUTHENT1A, trailer_block, self.KEY, uid)

        # Read the sector trailer block
        self.MFRC522.ReadTag(trailer_block)

        try:
            if status == self.MFRC522.MI_OK:
                # Prepare the data to be written
                data = bytearray()
                data.extend(bytearray(text.ljust(len(block_addr) * 16).encode('ascii')))
                i = 0
                for block_num in block_addr:
                    # Write the data to the corresponding data blocks
                    self.MFRC522.WriteTag(block_num, data[(i*16):(i+1)*16])
                    i += 1

            # Stop encryption
            self.MFRC522.StopCrypto1()

            # Return the tag ID and the written data
            return id, text[0:(len(block_addr) * 16)]
        except:
            # Stop encryption and return None if an exception occurs
            self.MFRC522.StopCrypto1()
            return None, None
    
    def write_designated (self, requests:list[WriteRequest], keys:tuple[tuple[int]]): #Assume requests is sorted (blocknum in increasing order)
        if len(requests)  == 0: return
        sector = requests[0].blocknum // 4
        prev = 0
        i = 1
        for i in range(1,len(requests)):
            if requests[i].blocknum // 4 != sector:
                #issue request
                trailer_block = sector * 4 + 3
                key = keys[sector]
                request = requests[prev:i]
                id, text_in = self.write_designated_no_block(request, key, trailer_block)

                while not id:
                    id, text_in = self.write_designated_no_block(request, key, trailer_block)

                sector = requests[i].blocknum
                prev = i
        
        if prev != i:
            trailer_block = sector * 4 + 3
            key = keys[sector]
            request = requests[prev:]
            id, text_in = self.write_designated_no_block(request, key, trailer_block)

            while not id:
                id, text_in = self.write_designated_no_block(request, key, trailer_block)


    def write_designated_no_block(self, requests:list[WriteRequest], key:tuple[int], trailer_block:int): 
        """
        Attempt to write data to the RFID tag.

        Args:
            text (str): The data to write.
            blockdata (list[tuple[int,list[int],tuple[int]]]): The block numbers of the data blocks to write.

        Returns:
            tuple: A tuple containing the tag ID (as an integer) and the data written (as a string), or (None, None) if the operation fails.
        """
        if not self._check_trailer_block(trailer_block):
            raise ValueError(f"Invalid Trailer Block {trailer_block}")

        for i in requests:
            if i.blocknum > trailer_block or i.blocknum < trailer_block - 3: raise ValueError(f"Invalid Write Request") 
        
        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None, None

        # Anticollision, return UID if success
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None, None

        # Convert UID to integer and store as id
        id = self._uid_to_num(uid)

        # Select the RFID tag using the UID
        self.MFRC522.SelectTag(uid)

        # Authenticate with the sector trailer block using the default key
        status = self.MFRC522.Authenticate(self.MFRC522.PICC_AUTHENT1A, trailer_block, key, uid)

        # Read the sector trailer block
        self.MFRC522.ReadTag(trailer_block)

        try:
            if status == self.MFRC522.MI_OK:
                # Prepare the data to be written
                for request in requests:
                    # Write the data to the corresponding data blocks
                    self.MFRC522.WriteTag(request.blocknum, request.data)

            # Stop encryption
            self.MFRC522.StopCrypto1()

            # Return the tag ID and the written data
            return id, request.data
        except:
            # Stop encryption and return None if an exception occurs
            self.MFRC522.StopCrypto1()
            return None, None

    def clear_sector(self, trailer_block):
        """
        Clear a sector of the RFID tag by writing zeros to all data blocks.

        Args:
            trailer_block (int): The block number of the sector trailer.

        Returns:
            int: The tag ID as an integer.
        """
        # Clear the sector using the clear_no_sector function
        id = self.clear_no_sector(trailer_block)

        # Retry clearing the sector until it succeeds and returns a tag ID
        while not id:
            id = self.clear_no_sector(trailer_block)

        # Return the tag ID
        return id

    def clear_sectors(self, trailer_blocks):
        """
        Clear multiple sectors of the RFID tag by writing zeros to all data blocks.

        Args:
            trailer_blocks (list): The list of block numbers of the sector trailers.

        Returns:
            int: The tag ID as an integer.
        """
        # Iterate through the trailer_blocks list and clear each sector
        for i in trailer_blocks:
            id = self.clear_sector(i)

        # Return the tag ID
        return id

    def clear_no_sector(self, trailer_block):
        """
        Clear a sector of the RFID tag by writing zeros to all data blocks.

        Args:
            trailer_block (int): The block number of the sector trailer.

        Returns:
            int: The tag ID as an integer, or None if the operation fails.
        """
        if not self._check_trailer_block(trailer_block):
            raise ValueError("Invalid Trailer Block {trailer_block}")

        block_addr = (trailer_block-3, trailer_block-2, trailer_block-1)

        # Send request to RFID tag
        (status, TagType) = self.MFRC522.Request(self.MFRC522.PICC_REQIDL)
        if status != self.MFRC522.MI_OK:
            return None

        # Anticollision, return UID if success
        (status, uid) = self.MFRC522.Anticoll()
        if status != self.MFRC522.MI_OK:
            return None

        # Convert UID to integer and store as id
        id = self._uid_to_num(uid)

        # Select the RFID tag using the UID
        self.MFRC522.SelectTag(uid)

        # Authenticate with the sector trailer block using the default key
        status = self.MFRC522.Authenticate(self.MFRC522.PICC_AUTHENT1A, trailer_block, self.KEY, uid)

        # Read the sector trailer block
        self.MFRC522.ReadTag(trailer_block)

        # Determine the block addresses of the data blocks in the sector

        try:
            if status == self.MFRC522.MI_OK:
                # Prepare data with all zeros
                data = [0x00]*16

                # Write zeros to each data block in the sector
                for block_num in block_addr:
                    self.MFRC522.WriteTag(block_num, data)

            # Stop encryption
            self.MFRC522.StopCrypto1()

            # Return the tag ID
            return id
        except:
            # Stop encryption and return None if an exception occurs
            self.MFRC522.StopCrypto1()
            return None

    def _check_trailer_block(self, trailer_block):
        if (trailer_block+1)%4 == 0:
            return True
        else:
            return False

    def _uid_to_num(self, uid):
        """
        Convert the UID (Unique Identifier) of the RFID tag to an integer.

        Args:
            uid (list): The UID as a list of bytes.

        Returns:
            int: The UID as an integer.
        """
        n = 0
        for i in range(0, 5):
            n = n * 256 + uid[i]
        return n

    def _split_string(self, string):
        """
        Split a string into chunks of 48 characters.

        Args:
            string (str): The string to split.

        Returns:
            list: A list of strings, each containing up to 48 characters.
        """
        l = list()
        for i in range(0, len(string), 48):
            l.append(string[i:i+48])

        # If the last chunk is less than 48 characters, pad it with null characters ('\0')
        if len(l[-1]) < 48:
            l[-1] += '\0'*(48-len(l[-1]))

        return l
