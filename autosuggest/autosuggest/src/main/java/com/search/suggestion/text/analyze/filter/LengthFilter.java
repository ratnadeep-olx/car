package com.search.suggestion.text.analyze.filter;

import com.search.suggestion.text.analyze.Analyzer;

import java.util.Collection;
import java.util.LinkedList;
import java.util.List;

import static com.search.suggestion.common.Precondition.checkPointer;

/**
 * Exclude text with length outside boundaries.
 */
public class LengthFilter extends Analyzer
{
    private final int min, max;

    /**
     * Constructs a new {@link LengthFilter}.
     */
    public LengthFilter(int min, int max)
    {
        this.min = min;
        this.max = max;
    }

    @Override
    public Collection<String> apply(Collection<String> input)
    {
        checkPointer(input != null);
        List<String> result = new LinkedList<>();
        for (String text : input)
        {
            checkPointer(text != null);
            if (text.length() >= min && text.length() <= max)
            {
                result.add(text);
            }
        }
        return result;
    }
}
